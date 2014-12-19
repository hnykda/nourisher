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

nour.data

#
# with open( "exp.json", "w" ) as ofile:
#     try:
#         import json
#         json.dump( nour.data, ofile )
#     except:
#         import pickle
#         pickle.dump( nour.data, ofile )
