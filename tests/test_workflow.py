import os
os.chdir( "../" )
print( os.path.abspath( "." ) )


testingUrl = 'http://www.huffingtonpost.com/news/authors/feed/'


from nourisher.nourisher import Nourisher

nour = Nourisher( testingUrl )

print( "adresa feedu: ", nour.origFeedUrl )

nour.collect_all()


from nourisher.collector.feeder import get_entries_info

print( nour.data )

print( type( nour.data ) )
print( nour.data.shape )

with open( "exp.json", "w" ) as ofile:
    ofile.write( nour.data.to_json() )
