from admin.utils import create_path, remove_old_archives
from acousticbrainz import config
import tarfile
import shutil
import os
import psycopg2
from datetime import datetime
import argparse

DUMP_CHUNK_SIZE = 1000


def dump_lowlevel_json(location=os.path.join(os.getcwd(), 'dump')):
    """Create JSON dumps with all low level documents."""

    temp_dir = '%s/temp' % location
    create_path(temp_dir)

    conn = psycopg2.connect(config.PG_CONNECT)
    conn2 = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()
    cur2 = conn.cursor()

    with tarfile.open("%s/acousticbrainz-lowlevel-json-%s-json.tar.bz2" % (location, datetime.today().strftime('%Y%m%d')), "w:bz2") as tar:
        last_mbid = ""
        index = 0
        print "  run queries..."
        cur.execute("""SELECT id FROM lowlevel ll ORDER BY mbid""")
        while True:
            id_list = cur.fetchmany(size = DUMP_CHUNK_SIZE)
            if not id_list:
                break

            id_list = tuple([ i[0] for i in id_list ])

            count = 0
            cur2.execute("SELECT mbid, data::text FROM lowlevel WHERE id IN %s ORDER BY mbid", (id_list,))
            while True:
                row = cur2.fetchone()
                if not row:
                    break

                mbid = row[0]
                json = row[1]

                if count == 0:
                    print "\r  write %s" % mbid,

                if mbid == last_mbid:
                    index += 1
                else:
                    index = 0

                filename = os.path.join(location, mbid + "-%d.json" % index)
                f = open(filename, "w")
                f.write(json)
                f.close()

                arcname = os.path.join("acousticbrainz-lowlevel-json-" + datetime.today().strftime('%Y%m%d'), "lowlevel", mbid[0:1], mbid[0:2], mbid + "-%d.json" % index)
                tar.add(filename, arcname=arcname)
                os.unlink(filename)

                last_mbid = mbid
                count += 1

        # Copying legal text
        tar.add("licenses/COPYING-PublicDomain", arcname=os.path.join("acousticbrainz-lowlevel-json-" + datetime.today().strftime('%Y%m%d'), 'COPYING'))

    shutil.rmtree(temp_dir)  # Cleanup


def dump_highlevel_json(location=os.path.join(os.getcwd(), 'dump')):
    """Create JSON dumps with all high level documents."""

    temp_dir = '%s/temp' % location
    create_path(temp_dir)

    conn = psycopg2.connect(config.PG_CONNECT)
    conn2 = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()
    cur2 = conn.cursor()

    with tarfile.open("%s/acousticbrainz-highlevel-json-%s-json.tar.bz2" % (location, datetime.today().strftime('%Y%m%d')), "w:bz2") as tar:
        last_mbid = ""
        index = 0
        print "  run queries..."
        cur.execute("""SELECT hl.id FROM highlevel hl, highlevel_json hlj WHERE hl.data = hlj.id ORDER BY mbid""")
        while True:
            id_list = cur.fetchmany(size = DUMP_CHUNK_SIZE)
            if not id_list:
                break

            id_list = tuple([ i[0] for i in id_list ])

            count = 0
            cur2.execute("""SELECT mbid, hlj.data::text
                             FROM highlevel hl, highlevel_json hlj
                            WHERE hl.data = hlj.id
                              AND hl.id IN %s
                            ORDER BY mbid""", (id_list, ))
            while True:
                row = cur2.fetchone()
                if not row:
                    break

                mbid = row[0]
                json = row[1]

                if count == 0:
                    print "\r  write %s" % mbid,

                if mbid == last_mbid:
                    index += 1
                else:
                    index = 0

                filename = os.path.join(location, mbid + "-%d.json" % index)
                f = open(filename, "w")
                f.write(json)
                f.close()

                arcname = os.path.join("acousticbrainz-highlevel-json-" + datetime.today().strftime('%Y%m%d'), "highlevel", mbid[0:1], mbid[0:2], mbid + "-%d.json" % index)
                tar.add(filename, arcname=arcname)
                os.unlink(filename)

                last_mbid = mbid
                count += 1

        # Copying legal text

    shutil.rmtree(temp_dir)  # Cleanup
        tar.add("licenses/COPYING-PublicDomain", arcname=os.path.join("acousticbrainz-highlevel-json-" + datetime.today().strftime('%Y%m%d'), 'COPYING'))
