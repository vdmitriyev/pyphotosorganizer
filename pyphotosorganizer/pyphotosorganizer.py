#!/usr/bin/env python

__author__      = "Viktor Dmitriyev"
__license__     = "MIT"
__version__     = "1.1.0"
__date__        = "04.06.2017"
__description__ = "Copy, sort and rename photos."

import os
import uuid
import shutil
import hashlib
import exifread
import datetime
import argparse
import subprocess
import logging.config

#
# Settings
#

# PATH-es
# SOURCE_PATH = 'd:\\tmp\\photos_renamer\\source\\'
# DESTINATION_PATH = 'd:\\tmp\\photos_renamer\\destination\\'

# LOGS_DIR = '.logs'

class PhotosRenamer:
    """ Copying, sorting and renaming photos. """

    def __init__(self, source, dest):
        """ Initial method. """

        self.SOURCE_PATH = source
        self.DESTINATION_PATH = dest

        self.initiate_env() # must be initiated before logging starts
        logging.config.fileConfig('logging.conf')
        self.log = logging.getLogger(__name__)


    def initiate_env(self):
        """ Pre processing """

        if not os.path.exists(self.SOURCE_PATH):
            log.info('Source path was not found')

        # check if destination path is existing create if not
        if not os.path.exists(self.DESTINATION_PATH):
            os.makedirs(self.DESTINATION_PATH)

        # creating logs folder
        logs_folder = '.logs'
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)

    def file_hash(self, filename):
        """ Compute file's hash function """

        # make a hash object
        h = hashlib.sha1()

        # open file for reading in binary mode
        with open(filename, 'rb') as file:
            # loop till the end of the file
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)

        return h.hexdigest() # hex representation of digest

    def photo_info(self, filename):
        """  Infos about photo's taken date"""

        # Read file
        open_file = open(filename, 'rb')

        # Return exif tags
        tags = exifread.process_file(open_file, stop_tag='Image DateTime')
        output = []

        try:
            # Grab date taken
            datetaken_string = tags['Image DateTime']
            datetaken_object = datetime.datetime.strptime(datetaken_string.values, '%Y:%m:%d %H:%M:%S')

            # Date
            day   = str(datetaken_object.day).zfill(2)
            month = str(datetaken_object.month).zfill(2)
            year  = str(datetaken_object.year)

            # Time
            second = str(datetaken_object.second).zfill(2)
            minute = str(datetaken_object.minute).zfill(2)
            hour   = str(datetaken_object.hour).zfill(2)

            # New Filename
            #output = [day, month, year, '{0}{1}{2}-{3}{4}{5}'.format(day, month, year, hour, minute, second)]
            output = [day, month, year, '{0}-{1}-{2}-{3}{4}'.format(year,month, day, hour, minute)]

        except Exception as ex:
            self.log.warning('Exception : {0}'.format(str(ex))) # intentionally "warning" and not "exception"

        return output

    def is_photo(self, _file):
        """ Checks whether it is a real photo or not"""

        if _file.lower().endswith('.jpg'):
            return True
        return False

    def process_new_extension(self, file, root):
        """ Processes files with new extensions """

        new_extension = file[file.rfind('.') + 1:].upper()
        new_extension_dest = os.path.join(self.DESTINATION_PATH, new_extension)

        # creating new destination folder
        if not os.path.exists(new_extension_dest):
            os.makedirs(new_extension_dest)

        source_file = os.path.join(root, file)
        dest_file = os.path.join(new_extension_dest, file)

        # if file with same name already was copied
        if os.path.exists(dest_file):
            #dest_file = '{0}-{1}.{2}'.format(dest_file, str(uuid.uuid1())[:5], new_extension)
            #dest_file = '{0}'.format(dest_file)
        #else:
            dest_file = '{0}-yet-another-copy.{1}'.format(dest_file[:-(len(new_extension)+1)], new_extension)

        shutil.copy2(source_file, dest_file)
        self.log.info('File with unrecognized extension: {0}, was copied to : {1}'.format(source_file, dest_file))

    def process_photos(self):

        dateinfo_prev = None # to store previous valid exif data

        # get all picture files from directory and process
        for root, _, files in os.walk(self.SOURCE_PATH):
            for file in files:
                self.log.info('Processing file: {0} (folder: {1})'.format(file, root))
                try:
                    if self.is_photo(file):
                        filename = os.path.join(root, file)
                        dateinfo = self.photo_info(filename)

                        if dateinfo == []:
                            if dateinfo_prev is None:
                                dateinfo = ['', 'UNKNOWN', 'UNKNOWN', str(uuid.uuid1())[:5]]
                            else:
                                dateinfo = dateinfo_prev
                        else:
                            dateinfo_prev = dateinfo

                        try:
                            out_filepath = os.path.join(self.DESTINATION_PATH, dateinfo[2], dateinfo[1])
                            out_filename = os.path.join(out_filepath, '{0}-{1}'.format(dateinfo[3], file))

                            # check if destination path is existing create if not
                            if not os.path.exists(out_filepath):
                                os.makedirs(out_filepath)

                            # copy the picture to the organized structure
                            if not os.path.exists(out_filename):
                                shutil.copy2(filename, out_filename)

                                # verify if new file is the same
                                if self.file_hash(filename) == self.file_hash(out_filename):
                                    self.log.info('Copied file with success to : {0}'.format(out_filename))
                                    #os.remove(filename)
                                else:
                                    self.log.info('Failed to copy file: {0}'.format(filename))
                            else:
                                self.log.info('File already existing: {0}'.format(out_filename))

                        except Exception as ex:
                            self.log.info('File has no exif, thus it skipped : {0}'.format(filename))
                            self.log.exception('Exception : {0}'.format(str(ex)))
                    else:
                        #log.info('File was skipped: {0}'.format(file))
                        self.process_new_extension(file, root)
                except Exception as ex:
                    self.log.exception('Exception : {0}'.format(str(ex)))

    # def bat_no_copied(self, files):
    #     """ Making BAT file for all files that were not copied """

    def check_photos(self):
        """ Check whether source and destination folders are consist. """

        dest_hashes = {}
        check_hashes = {}
        not_copied_files = list()

        # get all picture files from the source directory
        for root, _, files in os.walk(self.DESTINATION_PATH):
            for file in files:
                filename = os.path.join(root, file)
                dest_hashes[self.file_hash(filename)] = filename

        # get all picture files from the destination directory
        for root, _, files in os.walk(self.SOURCE_PATH):
            for file in files:
                filename = os.path.join(root, file)
                tmp_hash = self.file_hash(filename)
                if tmp_hash in dest_hashes:
                    check_hashes[tmp_hash] = True
                else:
                    check_hashes[tmp_hash] = False
                    not_copied_files.append(filename)

        if len(not_copied_files) > 0:
            self.log.info('File NOT YET copied:\n{0}'.format('\n'.join(not_copied_files)))
        else:
            self.log.info('All files from the source were copied into the destination folder')

def main(source, dest, mode):
    """ Main method that starts other methods.

    Arguments:
        source  {str} -- source folder
        dest    {str} -- destination folder
        mode    {str} -- mode to use the script - check of process
    """

    pr = PhotosRenamer(source=source, dest=dest)

    if mode == 'PROCESS':
        pr.process_photos()

    if mode == 'CHECK':
        pr.check_photos()

if __name__ == '__main__':

    # fetching input parameters
    parser = argparse.ArgumentParser(description='{0}\nVersion - {1}'.format(__description__, __version__))
    MODES = {'PROCESS', 'CHECK'}

    # source folder
    parser.add_argument(
        '--source',
        dest='source',
        help='path to a source folder')

    # destination folder
    parser.add_argument(
        '--dest',
        dest='dest',
        help='path to a destination folder')

    # mode
    parser.add_argument(
        '--mode',
        dest='mode',
        help='mode of the script, must be: ({0})'.format(','.join(MODES)))

    # parse input parameters
    args = parser.parse_args()

    if args.mode.upper() not in MODES:
        print ('Wrong parameters. Use command for further details -> --help')
        exit(0)

    main(args.source, args.dest, args.mode.upper())

