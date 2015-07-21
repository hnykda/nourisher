

__author__ = 'dan'

import time
import traceback
import sys
sys.path.append("../")

import logging
from logging.config import fileConfig

fileConfig('./logging_config.ini')
log = logging.getLogger()

def parse_arguments():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description="Program pro sber dat.", formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument( "-b", "--browser", choices = ["chrome", "chromium", "firefox", "phantomjs", "phantomjsTOR"], default = "phantomjs", help = "Which driver should be used" )
    parser.add_argument( "-d", "--debug", action="store_true", help = "Turn on debug mode." )
    parser.add_argument("-p", "--port", type=int, default=5432, help="Port of DB")
    parser.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="IP of DB")
    parser.add_argument("-l", "--log_level", type=str, help="Verbosity (not implemented yet!)")
    parser.add_argument("-a", "--articles_limit", type=int, default=50, help="Limit maximum processed articles (not implemented yet!)")
    parser.add_argument("-c", "--cleaning", action="store_true", help="Turn on cleaning (not implemented yet!)")
    parser.add_argument("-s", "--sleep", type=int, default=60, help="How many seconds we should wait between consequent collections")
    parser.add_argument("-m", "--mode", choices= ["remote", "local"], help="Activate local or remote mode", default="local")
    parser.add_argument("-n", "--database_name", type=str, required=True, help="Name of main database")
    parser.add_argument("-S", "--sources_collection", type=str, default="sources", help="Collection name with sources")
    parser.add_argument("-L", "--lock_collection", type=str, default="locks", help="Collection name for lock files")
    parser.add_argument("-D", "--data_collection", type=str, default="data", help="Collection name for output data")
    parser.add_argument("-E", "--error_collection", type=str, default="error", help="Collection name for error urls and their logs")

    return parser.parse_args()

#TODO:
# * Sbirani clanku by stalo za to zkusit vylepsit - udelat pokus s readability, goose, newspaper3k
# * dodelat uhadnuti jazyka
# * Cisteni dat nefunguje. zaslouzilo by to rewrite

def main():

    args = parse_arguments()
    if args.debug:
        log.setLevel(logging.DEBUG)
    log.debug("Log level set to {}".format(log.level))

    try:
        # from nourisher import settings
        # settings.DB_COLLECTION = args.collection
        # settings.DB_NAME = args.dbname
        # settings.DB_PORT = args.port
        # settings.DB_IP = args.ip
        # settings.DEFAULT_DRIVER = args.browser

        from nourisher.collects.collector import Collector
        collector = Collector(wdriver_name=args.browser)

        from nourisher.utiliser import fetch_doc_url_and_lock, get_db_driver
        db_driver = get_db_driver(args.dbname, args.ip, args.port)

        from nourisher.nourish import Nourisher

        document = fetch_doc_url_and_lock(db_driver, args.sources_collection, args.lock_collection)  # initial fetch

        counter = 0
        while document:
            url = document["orig_url"]

            now = time.time()
            log.info(str(counter) + ". Processing: " + url)
            try:
                nour = Nourisher(url)
                data = nour.collect_all(collector)

                log.debug("Updating document by data")
                document["data_raw"] = data

                log.debug("Adding document to data collection")
                db_driver[args.data_collection].insert(document)

                log.debug("Removing source URL from sources collection")
                db_driver[args.sources_collection].remove({"id_" : document["id_"]})
                time.sleep(args.sleep)

            except KeyboardInterrupt as ex:
                raise KeyboardInterrupt
            except ConnectionError as ex:
                log.error("Connection error. Exiting.")
                sys.exit(1)
            except Exception as ex:
                log.error("Cannot process.")
                log.error(sys.exc_info())
                tracb = traceback.format_exc()
                log.error(tracb)

                document["error_log"] = tracb
                db_driver[args.error_collection].insert(document)

                time.sleep(args.sleep)
            finally:
                log.info("It took:" + str(time.time() - now) + "s.\n----------\n")

                log.debug("Deleting lock file.")
                db_driver[args.lock_collection].remove({"id_" : document["id_"]})

            counter += 1
            document = fetch_doc_url_and_lock(db_driver, args.sources_collection, args.lock_collection)

    except KeyboardInterrupt as ex:
        log.warning("Termined by user.")
    except:
        print(sys.exc_info())
        tracb = traceback.format_exc()
        print(tracb)

if __name__ == "__main__":
    main()