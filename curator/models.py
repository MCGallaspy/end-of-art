from django.db import models

# Create your models here.
class Image(models.Model):
	isCurrent = models.BooleanField()
	path = models.FilePathField(path="/home/gallaspy/endOfArt/images", recursive=True)
	posVotes = models.IntegerField()
	negVotes = models.IntegerField()
	def __unicode__(self):
		return self.path
	def voteDiff(self):
		return self.posVotes - self.negVotes

class Figure(models.Model):
	image = models.ForeignKey(Image)
	polygons = models.TextField()
