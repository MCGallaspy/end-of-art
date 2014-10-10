from PIL import Image as PILImage, ImageDraw
from random import randint, shuffle, random
from models import Image
import re
import numpy as np
from scipy.spatial import Delaunay
from sympy import Poly, compose
from sympy.abc import x

# Some settings about the images
IMGWIDTH = 400 #pixels
IMGHEIGHT = 400
STATIC_FILE_DIR = "/home/gallaspy/endOfArt/curator/static/"
MUTATION_PROB = 0.4
COLOR_DEPTH = 2**8

# Generating sequences are nested lists of tuples like this:
# [ ( [(168, 123), (15, 41), (199, 255)], (219, 230, 174) ) ]
# The list of three 2-tuples represent the vertices of a triangle
# and the 3-tuple represents the rgb value of the triangle

class ImageGenerator():
	
	# eval() and literal_eval() seem to fail, so instead we'll
	# parse the string using some (lengthy) regex magic
	def _parseGenSeq(self, genSeqStr):
		# Define some regular expressions we might find useful
		# A 2-tuple
		twople = r"\(\d{1,3}, \d{1,3}\)"
		# The array of triangle vertices
		verts = r"\[" + (twople+r", ")*2 + twople + r"\]"
		# The RGB 3-tuple
		rgb = r"\(\d{1,3}, \d{1,3}, \d{1,3}\)"
		# A triangle, which is a 2-tuple containing the array of vertices and RGB 2-tuple
		triangle = r"\(" + verts + r", " + rgb + r"\)"
		trExpr = re.compile(triangle)
		twpleExpr = re.compile(twople)
		rgbExpr = re.compile(rgb)
		# Split the string into individual "triangles"
		triList = re.findall(trExpr, genSeqStr)
		# Then parse each triangle and add it to a list
		genSeqList = []
		for t in triList:
			vertStr = re.findall(twpleExpr,t)
			vertsData = []
			for v in vertStr:
				vertsData.append(eval(v))
			rgbStr = re.findall(rgbExpr,t)
			rgbData = eval(rgbStr[0])
			genSeqList.append( (vertsData, rgbData) )
		return genSeqList

	
	# Splice the generating sequences of 2 Images together and return a new Image with that seq
	def _splice(self, img1, img2):
		seq1 = self._parseGenSeq(img1.generatingSequence)		
		seq2 = self._parseGenSeq(img2.generatingSequence)
		cutNum = randint(0, min(len(seq1),len(seq2))-1)
		newSeq = seq1[0:cutNum]+seq2[cutNum:]
		for n in newSeq:
			self._triangleJumble(n)
		return Image(generatingSequence = str(newSeq))


	# Change the vertices and rgb values slightly of a generating sequence element. Modifies in place.
	def _triangleJumble(self, element):
		verts = element[0]
		rgb = element[1]
		newverts = []
		for v in verts:
			x = v[0]
			y = v[1]
			newx = int( x*(0.5 + random()) ) 
			newy = int( y*(0.5 + random()) ) 
			newverts.append((newx,newy))
		newr = max(0, min(255, rgb[0] + randint(-3,3)))
		newg = max(0, min(255, rgb[1] + randint(-3,3)))
		newb = max(0, min(255, rgb[2] + randint(-3,3)))
		newrgb = (newr, newg, newb)
		element = (newverts, newrgb)


	# Mutate an image: 50% chance of shuffle, 40% add triangle, 10% delete triangle
	def _old_mutate(self, img):
		prob = random();
		genSeq = self._parseGenSeq(img.generatingSequence)
		if prob < 0.5:
			shuffle(genSeq)
			img.generatingSequence = str(genSeq)
		elif prob < 0.9:
			genSeq.append(self._newTriangle())
			img.generatingSequence = str(genSeq)
		else:
			genSeq.remove( genSeq[randint(0,len(genSeq)-1)] )	
			img.generatingSequence = str(genSeq)
		return img

	
	# Mutates the funcstr in place by adding a random frequency
	def _mutate(self, funcstr):
		newFreq = self._getBasisFunctionStr()
		newfuncstr = ("lambda i,j: 0.5*((%(funcstr)s)(i,j) + (%(newFreq)s)(i,j))" %
			       { "funcstr": funcstr,
			       	 "newFreq": newFreq,
			       })
		funcstr = newfuncstr


	def _newTriangle(self):
		triVerts = []
		triVerts.append( ( randint(0,IMGWIDTH), randint(0,IMGHEIGHT) ) )
		triVerts.append( ( randint(0,IMGWIDTH), randint(0,IMGHEIGHT) ) )
		triVerts.append( ( randint(0,IMGWIDTH), randint(0,IMGHEIGHT) ) )
		color = ( randint(0,256), randint(0,256), randint(0,256) ) 
		return (triVerts, color)

	
	def _getBasisFunctionStr(self):
		ampl = 255/2.
		xfreq = randint(0,IMGWIDTH)/float(IMGWIDTH)
		yfreq = randint(0,IMGWIDTH)/float(IMGWIDTH)
		xphase = random()*3.14159
		yphase = random()*3.14159
		funcstr = ("lambda i,j: (%(ampl)s + %(ampl)s*0.5*(np.cos(2.*3.14159*%(xfreq)s*i + %(xphase)s)+np.cos(2.*3.14159*%(yfreq)s*j + %(yphase)s)))" %
			   { "ampl": ampl,
			     "xfreq": xfreq,
			     "xphase": xphase,
			     "yfreq": yfreq,
			     "yphase": yphase,
			   })
		return funcstr

	
	def _getRandQuadratic(self,mincoeff,maxcoeff):
		a = randint(mincoeff,maxcoeff)		
		b = randint(mincoeff,maxcoeff)		
		c = randint(mincoeff,maxcoeff)
		return Poly(a*x**2 + b*x + c, x)


	# Trying this baby again, but using a CAS to simplify 
	def _totallyNewBatch4(self):
		for i in range(0,20):
			relfilepath = "images/%(i)d.jpg" % {"i": i}
			newPILImg = PILImage.new('RGB', (IMGWIDTH,IMGHEIGHT))
			draw = ImageDraw.Draw(newPILImg)
			rfunc = self._getRandQuadratic(1, COLOR_DEPTH)
			gfunc = self._getRandQuadratic(0, COLOR_DEPTH)
			bfunc = self._getRandQuadratic(0, COLOR_DEPTH)
			for x in range(0,IMGWIDTH):
				for y in range(0,IMGHEIGHT):
					fill = (int(rfunc(x,y)), int(gfunc(x,y)), int(bfunc(x,y)))
					draw.point([x,y],fill)
			newPILImg.save(STATIC_FILE_DIR+relfilepath,'JPEG')
			newImg = Image()
			newImg.posVotes = 0
			newImg.negVotes = 0
			newImg.path = relfilepath
			newImg.isCurrent = True
			newImg.generatingSequence = str({ "rfunc": str(rfunc),
							  "gfunc": str(gfunc),
							  "bfunc": str(bfunc),
						    })
			newImg.save()		

	# Yet another approach where we color each pixel by a function on the coordinates
	def _totallyNewBatch3(self):
		for i in range(0,20):
			relfilepath = "images/%(i)d.jpg" % {"i": i}
			newPILImg = PILImage.new('RGB', (IMGWIDTH,IMGHEIGHT))
			draw = ImageDraw.Draw(newPILImg)
			rfuncstr = self._getBasisFunctionStr()
			gfuncstr = self._getBasisFunctionStr()
			bfuncstr = self._getBasisFunctionStr()
			rfunc = eval(rfuncstr)
			gfunc = eval(gfuncstr)
			bfunc = eval(bfuncstr)
			for x in range(0,IMGWIDTH):
				for y in range(0,IMGHEIGHT):
					fill = (int(rfunc(x,y)), int(gfunc(x,y)), int(bfunc(x,y)))
					draw.point([x,y],fill)
			newPILImg.save(STATIC_FILE_DIR+relfilepath,'JPEG')
			newImg = Image()
			newImg.posVotes = 0
			newImg.negVotes = 0
			newImg.path = relfilepath
			newImg.isCurrent = True
			newImg.generatingSequence = str({ "rfunc": rfuncstr,
							  "gfunc": gfuncstr,
							  "bfunc": bfuncstr,
						    })
			newImg.save()		

		
	# Let's take a new approach in order to make more visually compelling images
	# Tiles the entire image with non-overlapping triangles using the Delaunay algorithm
	def _totallyNewBatch2(self):
		for i in range(0,100):
			# First add the four corners
			points = [[0,0], [0,IMGHEIGHT], [IMGWIDTH,0], [IMGWIDTH,IMGHEIGHT]]
			# Then a bunch of random points
			for j in range(0,300):
				points.append( [randint(0,IMGWIDTH), randint(0,IMGHEIGHT)] )
			# We'll need to use a numpy array object
			nppoints = nparray(points)
			tri = Delaunay(nppoints)
			# nppoints[tri.vertices] will return a numpy array where each element is a list of vertices
			triangles = []
			for x in nppoints[tri.vertices]:
				rgb = (randint(0,255), randint(0,255), randint(0,255))
				verts = [(x[0][0], x[0][1]), (x[1][0], x[1][1]), (x[2][0], x[2][1])]
				triangles.append((verts,rgb))
			# Now lets draw it
			relfilepath = "images/%(i)d.jpg" % {"i": i}
			newPILImg = PILImage.new('RGB', (IMGWIDTH,IMGHEIGHT))
			draw = ImageDraw.Draw(newPILImg)
			for t in triangles:
				draw.polygon(t[0], fill=t[1])
			newPILImg.save(STATIC_FILE_DIR+relfilepath,'JPEG')
			newImg = Image()
			newImg.posVotes = 0
			newImg.negVotes = 0
			newImg.path = relfilepath
			newImg.isCurrent = True
			newImg.generatingSequence = str(triangles)
			newImg.save()	
			

	def _totallyNewBatch(self):
		for i in range(0,100):
			relfilepath = "images/%(i)d.jpg" % {"i": i}
			newPILImg = PILImage.new('RGB', (IMGWIDTH,IMGHEIGHT))
			draw = ImageDraw.Draw(newPILImg)
			drawSeq = []
			newImg = Image()
			for m in range(0,800):
				drawSeq.append(self._newTriangle())
			for e in drawSeq:
				draw.polygon(e[0], fill=e[1])
			newPILImg.save(STATIC_FILE_DIR+relfilepath,'JPEG')
			newImg.posVotes = 0
			newImg.negVotes = 0
			newImg.path = relfilepath
			newImg.isCurrent = True
			newImg.generatingSequence = str(drawSeq)
			newImg.save()	
	
	def breed(self, curBatch, numNewImgs):
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
			img1 = orderedImgs[n1]
			img2 = orderedImgs[n2]
			rfunc1str = eval(img1.generatingSequence)["rfunc"]
			rfunc2str = eval(img2.generatingSequence)["rfunc"]
			newrfuncstr = ("lambda i,j: 0.5*((%(rfunc1str)s)(i,j) + (%(rfunc2str)s)(i,j))" %
				       { "rfunc1str": rfunc1str,
				       	 "rfunc2str": rfunc2str,
				       })
			gfunc1str = eval(img1.generatingSequence)["gfunc"]
			gfunc2str = eval(img2.generatingSequence)["gfunc"]
			newgfuncstr = ("lambda i,j: 0.5*((%(gfunc1str)s)(i,j) + (%(gfunc2str)s)(i,j))" %
				       { "gfunc1str": gfunc1str,
				       	 "gfunc2str": gfunc2str,
				       })
			bfunc1str = eval(img1.generatingSequence)["bfunc"]
			bfunc2str = eval(img2.generatingSequence)["bfunc"]
			newbfuncstr = ("lambda i,j: 0.5*((%(bfunc1str)s)(i,j) + (%(bfunc2str)s)(i,j))" %
				       { "bfunc1str": bfunc1str,
				       	 "bfunc2str": bfunc2str,
				       })
			# Mutate the generating functions randomly
			prob = random()
			if prob < MUTATION_PROB:
				self._mutate(newrfuncstr)
				self._mutate(newbfuncstr)
				self._mutate(newgfuncstr)
			rfunc = eval(newrfuncstr)
			gfunc = eval(newgfuncstr)
			bfunc = eval(newbfuncstr)
			for x in range(0,IMGWIDTH):
				for y in range(0,IMGHEIGHT):
					fill = (int(rfunc(x,y)), int(gfunc(x,y)), int(bfunc(x,y)))
					draw.point([x,y],fill)
			newPILImg.save(STATIC_FILE_DIR+relfilepath,'JPEG')
			newImg = Image()
			newImg.posVotes = 0
			newImg.negVotes = 0
			newImg.path = relfilepath
			newImg.isCurrent = False
			newImg.generatingSequence = str({ "rfunc": newrfuncstr,
							  "gfunc": newgfuncstr,
							  "bfunc": newbfuncstr,
						       })
			newBatch.append(newImg)
		return newBatch
	
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

