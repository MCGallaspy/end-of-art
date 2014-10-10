from models import Image
from random import randint
from ImageGenerator import ImageGenerator

# Returns a random image from the set of currently being-voted-on images
def getRandomImage():
	curImgsQuery = Image.objects.filter(isCurrent=True)
	i = randint(0, curImgsQuery.count()-1)
	return curImgsQuery[i]

def voteUp(img):
	img.posVotes += 1

def voteDown(img):
	img.negVotes += 1

# Return a list of images as opposed to the QuerySet itself.
def currentBatch():
	query = Image.objects.filter(isCurrent=True)
	imgs = []
	for q in query:
		imgs.append(q)
	return imgs

# Invokes the image generator, retires the current batch (isCurrent set to false)
# and 
def setNewBatch():
	curBatch = currentBatch()
	numNewImgs = len(curBatch)
	gen = ImageGenerator()
	newBatch = gen.breed(curBatch, numNewImgs)
	for img in newBatch:
		img.isCurrent = True
		img.save()
	for img in curBatch:
		img.isCurrent = False
		img.save()
