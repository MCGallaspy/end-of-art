# Create your views here.
from models import Image
from django.template import Context, loader, RequestContext
from django.http import HttpResponse
from functions import getRandomImage, voteUp, voteDown

def index(request):
	if request.method == "POST":
		imgid = request.POST['imgid']
		lastimg = Image.objects.get(id=imgid)
		if request.POST['vote']=='upvote':
			voteUp(lastimg)	
		else:
			voteDown(lastimg)
		lastimg.save()
	img = getRandomImage()
	t = loader.get_template('curator/index.html')
	c = RequestContext(request, {'img': img, })
	return HttpResponse(t.render(c))
