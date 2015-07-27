__author__ = 'dan'

import time
import traceback
from random import randint

def parse_arguments():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description="Program pro sber dat.", formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument( "-b", "--browser", choices = ["chrome", "chromium", "firefox", "phantomjs", "phantomjsTOR"], default = "phantomjs", help = "Which driver should be used" )
    parser.add_argument( "-d", "--debug", action="store_true", help = "Turn on debug mode." )
    parser.add_argument("-p", "--port", type=int, default=5432, help="Port of DB")
    parser.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="IP of DB")
    parser.add_argument("-l", "--log_level", type=int, choices=[10,20,30,40,50], default=20, help="Log level of standard_output. Debug ~ 10, Critical ~ 50. In logfile, there is always DEBUG.")
    parser.add_argument("--stdout", type=str, default="nour.log", help="Path to standard logfile. If 'stdout', then output is to console")
    parser.add_argument("-o", "--output_logfile", type=str, default="debug.log", help="Path to debug logfile (used by watchdog).")
    parser.add_argument("-a", "--articles_limit", type=int, default=50, help="Limit maximum processed articles (not implemented yet!)")
    parser.add_argument("-c", "--cleaning", action="store_true", help="Turn on cleaning (not implemented yet!)")
    parser.add_argument("-u", "--url", type=str, default=None, help="Process this specific url from database.")
    parser.add_argument("-s", "--sleep", type=int, default=60, help="Time in seconds between consequent collections. It's in interval (sleep, 2*sleep)")
    parser.add_argument("-n", "--database_name", type=str, required=True, help="Name of main database")
    parser.add_argument("-r", "--random", action="store_true", help="If sources should be processed in random order")
    parser.add_argument("-S", "--sources_collection", type=str, default="sources", help="Collection name with sources")
    parser.add_argument("-L", "--lock_collection", type=str, default="locks", help="Collection name for lock files")
    parser.add_argument("-D", "--data_collection", type=str, default="data", help="Collection name for output data")
    parser.add_argument("-E", "--error_collection", type=str, default="error", help="Collection name for error urls and their logs")
    parser.add_argument("-e", "--ignore_error_check", action="store_true", default=False, help="If True, then no check is done for URL if it throws an error in  past.")
    parser.add_argument("-x", "--xvfb", action="store_true", default=False, help="If True, run in xvfb mode - then even on headless server X browsers can be used.")
    #parser.add_argument("-R", "--restart_driver", type=int, help="How often should be driver reinitialized. (good for clearing cache and fighting phantomjs memory consumption)")

    return parser.parse_args()

def prepare_logging(level, logfile, stdoutput):

    import logging

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    logFormatter = logging.Formatter("%(asctime)s %(name)-8s %(levelname)-4s %(message)s", datefmt="%Y%m%d %H:%M:%S")
    log = logging.getLogger()

    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(10)  # file always set to 10
    log.addHandler(fileHandler)

    if stdoutput == "stdout":
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        consoleHandler.setLevel(level)
        log.addHandler(consoleHandler)
    else:
        fileHandler = logging.FileHandler(stdoutput)
        fileHandler.setFormatter(logFormatter)
        fileHandler.setLevel(level)  # file always set to 10
        log.addHandler(fileHandler)


    log.setLevel(0)

    #log.debug("Standard logile, respective debug logfile log level set to {}, {}".format(consoleHandler.level, fileHandler.level))

    return log

def main():

    args = parse_arguments()
    log = prepare_logging(args.log_level, args.output_logfile, args.stdout)

    if args.xvfb:
        from xvfbwrapper import Xvfb

        vdisplay = Xvfb()
        vdisplay.start()


    try:
        import settings
        settings.ARTICLES_LIMIT = args.articles_limit
        # settings.DB_COLLECTION = args.collection
        # settings.DB_NAME = args.dbname
        # settings.DB_PORT = args.port
        # settings.DB_IP = args.ip
        # settings.DEFAULT_DRIVER = args.browser

        from collects.collector import Collector
        collector = Collector(wdriver_name=args.browser)

        from utiliser import fetch_doc_url_and_lock, get_db_driver
        db_driver = get_db_driver(args.database_name, args.ip, args.port)

        from nourish import Nourisher

        if args.url is None:
            document = fetch_doc_url_and_lock(db_driver, args.sources_collection, args.lock_collection,
                                              args.error_collection, args.random, args.ignore_error_check)  # initial fetch
        else:
            document = db_driver["orig_sources"].find_one({"orig_url" : args.url})

        counter = 1
        while document:
            url = document["orig_url"]

            now = time.time()
            log.info(str(counter) + ". Processing: " + url)
            try:
                #if args.restart_driver and (counter % args.restart_driver == 0):
                #    collector.restart_driver()
                #    log.debug("Restarting driver.")

                nour = Nourisher(url)
                data = nour.collect_all(collector)

                if args.url is None:
                    log.debug("Updating document by data")
                    document["data_raw"] = data

                    log.debug("Adding document to data collection")
                    db_driver[args.data_collection].insert(document)

                    log.debug("Removing source URL from sources collection")
                    db_driver[args.sources_collection].remove({"_id" : document["_id"]})
                else:
                    log.info("Data collected, but URL switch is ON so I discard them and end.")
            except KeyboardInterrupt as ex:
                log.warning("Keyboard interrupted.")
                raise KeyboardInterrupt
            except Exception as ex:
                log.error("Cannot process. Error: \n", exc_info=True)
                tracb = traceback.format_exc()

                document["error_log"] = tracb
                idecko = document.pop("_id")  # chyby se muzou objevit nekolikrat u stejneho _id (pri ruznem procesovani), tudiz musi mit sve vlastni
                db_driver[args.error_collection].insert(document)

                # this is because of finally block - removing the lock file
                document["_id"] = idecko

            finally:
                log.debug("Deleting lock file.")
                db_driver[args.lock_collection].remove({"_id" : document["_id"]})

                log.info("Whole processing took: {}s. Now sleeping for {}s".format(str(time.time() - now), args.sleep))

                if args.url is not None:
                    import sys
                    sys.exit(0)

                time.sleep(randint(args.sleep, 2 * args.sleep))
            counter += 1
            document = fetch_doc_url_and_lock(db_driver, args.sources_collection, args.lock_collection,
                                              args.error_collection, args.random, args.ignore_error_check)
    except KeyboardInterrupt as ex:
        log.warning("Terminated by user.")
    except SystemExit as ex:
        log.info("Finished. Exiting")

if __name__ == "__main__":
    main()
