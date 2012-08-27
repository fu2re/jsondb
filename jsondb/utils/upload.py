import urllib2
import poster

def upload_file(file_local_address, tags, project, key):
    poster.streaminghttp.register_openers()
    data = {
        "file": open(file_local_address, "rb"),
        'key':key,
        'tags':tags,
        'project':project,
    }
#    print data
    datagen, headers = poster.encode.multipart_encode(data)


    request = urllib2.Request("http://test.addictedcompany.com/storage/post/", datagen, headers)
    return urllib2.urlopen(request).read()