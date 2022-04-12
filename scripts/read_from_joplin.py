
import pathlib
import urllib3 as url
from urllib3 import HTTPResponse
import json
import datetime
import os

token = "69cdbc30560158649c7d8703aeb4c03166f74668e5dbb0b897402c7e15fd8e0ab076b1bfbde9bf0218d1438b9d43ca33c107418203d0b6ca204ec2fc8da00281"
url_get_all_notes = "http://localhost:41184/notes?token={token}&fields=id,parent_id,title,created_time,body".format(token=token)
url_get_tags_base = "http://localhost:41184/notes/{id}/tags?token={token}&fields=title"
url_get_folder_base = "http://localhost:41184/folders/{id}?token={token}&fields=title"
url_get_resources_base = "http://localhost:41184/notes/{id}/resources?token={token}"
url_get_file_base = "http://localhost:41184/resources/{id}/file?token={token}"

f_path = pathlib.Path(__file__)
content_path = f_path.parent/".."/"content"


requestor = url.PoolManager(num_pools=8)


r:HTTPResponse = requestor.request("GET",url_get_all_notes)
s = str(r.data,encoding="utf-8")
notes = json.loads(s)
items = notes["items"]


for item in items:
    # meta
    id = item["id"]
    parent_id = item["parent_id"]

    title = item["title"]
    time_stamp = item["created_time"]/1000
    date = str(datetime.datetime.fromtimestamp(time_stamp))
    
    # tags
    response = requestor.request("GET",url_get_tags_base.format(id=id,token=token))
    tag_items = json.loads(str(response.data,encoding="utf-8"))["items"]
    tags = []
    dont = False

    for tag_item in tag_items:
        tag = tag_item["title"]
        if tag == "to-do":
            dont = True
            break
        tags.append(tag)

    if dont:
        continue

    tags = ",".join(tags)

    # category

    response = requestor.request("GET",url_get_folder_base.format(id=parent_id,token=token))
    folder = json.loads(str(response.data,encoding="utf-8"))

    category = folder["title"]

    headings = ["---","title:"+title,"tags:"+tags,"date:"+date,"category:"+category,"author:libMan","---"]

    # handling resources

    response = requestor.request("GET",url_get_resources_base.format(id=id,token=token))
    resources = json.loads(str(response.data,encoding="utf-8"))

    for image_item in resources["items"]:
        image_title = image_item["title"]
        image_id = image_item["id"]
        image_suffix = pathlib.Path(image_title).suffix

        image_path:pathlib.Path = content_path/"images"/(str(image_id)+image_suffix)

        if not image_path.parent.exists():
            image_path.parent.mkdir()

        response = requestor.request("GET",url_get_file_base.format(id=image_id,token=token))

        item["body"] = item["body"].replace(":/"+str(image_id),"images/"+str(image_id)+image_suffix)

        image_path.write_bytes(response.data)
    
    # write md file

    heading_to_write = "\n".join(headings)
    path:pathlib.Path = content_path/(title+".md")

    f = path.open("w+",encoding="utf-8")
    f.write(heading_to_write)
    f.write("\n")
    f.write(item["body"])









    


    
