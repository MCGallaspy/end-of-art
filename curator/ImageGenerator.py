from PIL import Image as PILImage, ImageDraw
from random import randint, random
from models import Image, Figure
from math import atan2, sqrt

# Some settings about the images
IMGWIDTH = 400 #pixels
IMGHEIGHT = 400
STATIC_FILE_DIR = "/home/gallaspy/endOfArt/curator/static/"
MUTATION_PROB = 0.4
COLOR_DEPTH = 2**8

class ImageGenerator():

	# Create a polygon with a random number of vertices
	# If boundVerts != [] then make sure the polygon is kind of inside
	# those vertices.
	@staticmethod
	def _randPolygon(boundVerts=[]):
		verts = []

		if boundVerts != []:
			xmax = max(map(lambda t: t[0], boundVerts))
			ymax = max(map(lambda t: t[1], boundVerts))
			xmin = min(map(lambda t: t[0], boundVerts))
			ymin = min(map(lambda t: t[1], boundVerts))
		else:
			xmax = IMGWIDTH
			ymax = IMGHEIGHT
			xmin = 0
			ymin = 0

		while True:
			x = randint(xmin, xmax)
			y = randint(ymin, ymax)
			verts.append((x,y))
			if random() < 0.5 and len(verts) >= 3:
				break;

		rgb = (randint(0,COLOR_DEPTH), randint(0,COLOR_DEPTH), randint(0,COLOR_DEPTH))
	
		# To ensure no self-intersecting polygons
		verts = convexHull(verts)
		
		return (verts, rgb)

	# Okay, trying a whole new approach to generating images
	@staticmethod
	def _bootstrapImages():
		for i in range(0,20):
			figures = []
			while len(figures) <= 2 or random() < 0.5:
				polygons = []
				polygons.append(ImageGenerator._randPolygon())
				while random() < 0.8:
					lastPolyVerts = polygons[-1][0]
					polygons.append(ImageGenerator._randPolygon(lastPolyVerts))
				figures.append(polygons)
			relfilepath = "images/%(i)d.jpg" % {"i": i}
			newPILImg = PILImage.new('RGB', (IMGWIDTH,IMGHEIGHT))
			draw = ImageDraw.Draw(newPILImg)
			for f in figures:
				for p in f:
					print f
					print p
					verts = p[0]
					rgb = p[1]
					draw.polygon(verts, fill=rgb)
			newPILImg.save(STATIC_FILE_DIR+relfilepath,'JPEG')
			newImg = Image()
			newImg.posVotes = 0
			newImg.negVotes = 0
			newImg.path = relfilepath
			newImg.isCurrent = True
			newImg.save()
			for f in figures:
				newFig = Figure()
				newFig.image = newImg
				newFig.polygons = str(f)
				newFig.save()
	
	@staticmethod
	def breed(curBatch, numNewImgs):
		return 0	

	def _old_breed(self, curBatch, numNewImgs):
		#First sort the curBatch by the method voteDiff, then take the top 3/4
		orderedImgs = sorted(curBatch, key=lambda img: -1*img.voteDiff())
		maxind = int( 0.75*len(orderedImgs) )
		orderedImgs = orderedImgs[0:maxind]
		newBatch = []
		for i in range(0,numNewImgs):
			relfilepath = "images/%(i)d.jpg" % {"i": i}
			newPILImg = PILImage.new('RGB', (IMGWIDTH,IMGHEIGHT))
			draw = ImageDraw.Draw(newPILImg)
			# Create a new generating sequence from the old ones
			n1 = randint(0,maxind-1)
			n2 = randint(0,maxind-1)
			newImg = self._splice( orderedImgs[n1], orderedImgs[n2] )
			prob = random()
			if prob < MUTATION_PROB:
				self._mutate(newImg)
			drawSeq = self._parseGenSeq(newImg.generatingSequence)
			for e in drawSeq:
				draw.polygon(e[0], fill=e[1])
			newPILImg.save(STATIC_FILE_DIR+relfilepath,'JPEG')
			newImg.posVotes = 0
			newImg.negVotes = 0
			newImg.path = relfilepath
			newImg.isCurrent = False
			newBatch.append(newImg)
		return newBatch

# Determine the convex hull of a set of points using Graham scan algorithm
# Stupid scipy version 0.10.1 doesn't have it... Damn you Debian stable repositories!
def convexHull(points):

	# First find the point with the lowest y and x coordinates. Call it P.
	def cmprPnts(q1, q2):
		if q1[1] < q2[1]:
			return q1
		elif q1[1] == q2[1]:
			if q1[0] < q2[0]:
				return q1
			else:
				return q2
		else:
			return q2

	# Find the bottom left-est point and put it first in the array
	# and sort all the other points by angle
	P = reduce(cmprPnts, points)
	points.remove(P)
	def angle(Q):
		return atan2(Q[1]-P[1], Q[0]-P[0])
	points.sort(key=angle)
	points.insert(0,P)
	points.append(P)

	#Then we check each successive triple of pts for left turns or right turns
	def leftTurn(q1, q2, q3):
		val = (q2[0]-q1[0])*(q3[1]-q1[1]) - (q2[1]-q1[1])*(q3[0]-q1[0])
		if val >= 0:
			return True
		else:
			return False
	hull = [P]
	for i in range(1, len(points)-1):
		hull.append(points[i])
		q1 = hull[-2]
		q2 = hull[-1]
		q3 = points[i+1]
		if not leftTurn(q1,q2,q3):
			hull.pop()	
	return hull	
