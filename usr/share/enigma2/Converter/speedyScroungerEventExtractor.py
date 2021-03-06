from Components.Converter.Converter import Converter
from Components.Element import cached
import re
import HTMLParser

#Version 1.0.0
class speedyScroungerEventExtractor (Converter, object):
	#Input Parameter vom skin - getrennt durch ein Komma
	EPISODE_NUM = "EpisodeNum"
	SUBTITLE = "Subtitle"					#Skin Parameter: Subtitle(maxWords) -> z.B. mit 'Subtitle(10)' werden nur Subtitles mit max. 10 Woertern angezeigt
	PARENTAL_RATING = "ParentalRating"
	
	#Parser fuer Serien- und Episodennummer
	seriesNumParserList = [('(\d+)[.]\sStaffel[,]\sFolge\s(\d+)'), 
							_('(\d+)[.]\sStaffel[,]\sEpisode\s(\d+)'),
							_('(\d+)[.]\sEpisode\sder\s(\d+)[.]\sStaffel')]
	
	def __init__(self, type):
		Converter.__init__(self, type)

		#Input Argumente vom Skin
		self.types = str(type).split(",")
		self.logType = None

	@cached
	def getText(self):
		event = self.source.event
		h = HTMLParser.HTMLParser()
		if event is not None:
			if self.types != '':
				rets = []
				try:
					for type in self.types:
						type.strip()
						self.logType = type
						if type == self.EPISODE_NUM:
							episodeNum = self.getEpisodeNum(event)
							if episodeNum != "" and len(episodeNum) > 0:
								rets.append(episodeNum)
						elif self.SUBTITLE in type:
							try:
								maxWords = int(self.getMaxSubtitleWords(type))
								subTitle = self.getSubtitle(event, maxWords)
								if subTitle != "" and len(subTitle) > 0:						
									rets.append(subTitle)
							except:
								rets.append(self.getSubtitle(event, maxWords))
						elif type == self.PARENTAL_RATING:
							rating = event.getParentalData()
							if not rating is None:
								rating = rating.getRating()
								if rating > 0:
									rets.append("FSK %d" % (rating))
						else:
							rets.append("!!! invalid type '%s' !!!" % (type))

					sep = ' %s ' % str(h.unescape('&#xB7;'))
					return sep.join(rets)
				except Exception, e:
					return "[Error] getText: '%s'  %s" % (self.logType, str(e))
		return ""
	text = property(getText)

	def getFullDescription(self, event):
		desc = None
		ext_desc = event.getExtendedDescription()
		short_desc = event.getShortDescription()
		if short_desc == "":
			return ext_desc
		elif ext_desc == "":
			return short_desc
		else:
			return "%s\n\n%s" % (short_desc, ext_desc)

	def getEpisodeNum(self, event):
		desc = self.getFullDescription(event)

		for parser in self.seriesNumParserList:
			extractSeriesNums = re.search(parser, desc)

			if(extractSeriesNums):
				sNum = extractSeriesNums.group(1)
				eNum = extractSeriesNums.group(2)

				return 'S%sE%s' % (sNum.zfill(2), eNum.zfill(2))

		return ""

	def getMaxSubtitleWords(self, type):
		maxSubtitleWordsParser = 'Subtitle[(](\d+)[)]'
		maxSubtitleWords = re.search(maxSubtitleWordsParser, type)
		
		if(maxSubtitleWords):
			return maxSubtitleWords.group(1)
		else:
			return "!!! invalid type '%s' !!!" % (type)
			
	def getSubtitle(self, event, maxWords):
		try:
			short_desc = event.getShortDescription()
			if short_desc != "":
				wordList = short_desc.split(" ")
				if len(wordList) <= maxWords:
					del wordList[maxWords:len(wordList)]
					sep = ' '
					return sep.join(wordList)
			else:
				return ""
		except Exception, e:
			return "[Error] getSubtitle: %s" % (str(e))
		
		return ""