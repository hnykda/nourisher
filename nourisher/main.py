__author__ = 'dan'

import time
import traceback
import sys

import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')
log = logging.getLogger()

def parse_arguments():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description="Program pro sber dat.", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument( "-b", "--browser", choices = ["chrome", "chromium", "firefox", "phantomjs", "phantomjsTOR"], default = "phantomjs", help = "Which driver should be used" )
    parser.add_argument( "-d", "--debug", action="store_true", help = "Turn on debug mode." )
    parser.add_argument("-c", "--collection", type=str, default="sber", help="Name of collection in DB")
    parser.add_argument("-n", "--dbname", type=str, default="testdb", help="Name of DB")
    parser.add_argument("-p", "--port", type=int, default=5432, help="Port of DB")
    parser.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="IP of DB")
    parser.add_argument("-l", "--log_level", type="str", help="Verbosity (not implemented yet!)")
    parser.add_argument("-u", "--url_input", type="str", required=True,help="Path to file with URLs with feed addresses to collect. One URL per line")
    parser.add_argument("-s", "--sleep", type=int, default=60, help="How many seconds we should wait between consequent collections")

    return parser.parse_args()

def load_data(pth):
    with open(pth, "r") as ifile:
        r = ifile.readlines()
    return r

def main():

    args = parse_arguments()
    if args.debug:
        log.setLevel(logging.DEBUG)
    log.debug("Log level set to {}".format(log.level))
    try:
        from nourisher import settings
        settings.VERBOSITY = 1
        settings.DB_COLLECTION = args.collection
        settings.DB_NAME = args.dbname
        settings.DB_PORT = args.port
        settings.DB_IP = args.ip
        settings.get_setings()
        from nourisher.nourisher import Nourisher

        urls = load_data(args.url_input)
        counter = 0
        dobre = []
        spatne = []
        for url in urls:
            now = time.time()
            print(counter, "Beru: ", url)
            try:
                nour = Nourisher(url)
                nour.collect_all()
                nour.retrieve_data()
                nour.clean_data()
                nour.update_object_db("cleaned", nour.dataCleaned)
                dobre.append(url)
                print("Zabralo to:", time.time() - now, "sekund.\n----------\n")
                time.sleep(args.sleep)
            except:
                print(sys.exc_info())
                tracb = traceback.format_exc()
                print(tracb)
                spatne.append((url, tracb))
                print("Zabralo to:", time.time() - now, "sekund.\n----------\n")
            counter += 1
    except KeyboardInterrupt as ex:
        log.warning("Termined by user.")
    except:
        print(sys.exc_info())
        tracb = traceback.format_exc()
        print(tracb)
        spatne.append((url, tracb))
        print("Zabralo to:", time.time() - now, "sekund.\n----------\n")
    finally:
        import json
        with open("spatne_url.txt", "w") as ofile:
            json.dump(spatne, ofile)
        with open("dobre_url.txt", "w") as ofile:
            json.dump(dobre, ofile)

if __name__ == "__main__":
    main()