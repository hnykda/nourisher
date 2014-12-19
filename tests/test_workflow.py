import os
os.chdir( "../" )
print( os.path.abspath( "." ) )

testingUrl = 'http://www.huffingtonpost.com/news/authors/feed/'

from nourisher.nourisher import Nourisher

nour = Nourisher( testingUrl )

print( "adresa feedu: ", nour.origFeedUrl )

nour.collect_all()

lks = nour.data[1]

from nourisher.collector.feeder import get_entries_info


get_entries_info( lks )
