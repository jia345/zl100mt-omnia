#
# foris-controller
# Copyright (C) 2017 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import pytest
import random
import time

from foris_controller.utils import RWLock


class Locker(object):
    PLACE_BEGIN = 'B'
    PLACE_END = 'E'
    KIND_READ = 'R'
    KIND_WRITE = 'W'

    def __init__(self, locking_module, entity_object, output):
        self.lock = RWLock(locking_module)
        self.output = output
        self._output_lock = locking_module.Lock()
        self.entity = entity_object

    def store_log(self, kind, place):
        with self._output_lock:
            self.output.append((kind, place))


@pytest.fixture(params=["threading", "multiprocessing"], scope="function")
def locker_instance(request):
    if request.param == "threading":
        import threading
        output = []
        locker = Locker(threading, threading.Thread, output)
    elif request.param == "multiprocessing":
        import multiprocessing
        manager = multiprocessing.Manager()
        output = manager.list()
        locker = Locker(multiprocessing, multiprocessing.Process, output)
    yield locker



def test_locks_single(locker_instance):
    with locker_instance.lock.readlock:
        locker_instance.store_log(locker_instance.KIND_READ, locker_instance.PLACE_BEGIN)
        locker_instance.store_log(locker_instance.KIND_READ, locker_instance.PLACE_END)

    with locker_instance.lock.writelock:
        locker_instance.store_log(locker_instance.KIND_WRITE, locker_instance.PLACE_BEGIN)
        locker_instance.store_log(locker_instance.KIND_WRITE, locker_instance.PLACE_END)

    with locker_instance.lock.readlock:
        locker_instance.store_log(locker_instance.KIND_READ, locker_instance.PLACE_BEGIN)
        locker_instance.store_log(locker_instance.KIND_READ, locker_instance.PLACE_END)

    with locker_instance.lock.writelock:
        locker_instance.store_log(locker_instance.KIND_WRITE, locker_instance.PLACE_BEGIN)
        locker_instance.store_log(locker_instance.KIND_WRITE, locker_instance.PLACE_END)

    assert list(locker_instance.output) == [
        (locker_instance.KIND_READ, locker_instance.PLACE_BEGIN),
        (locker_instance.KIND_READ, locker_instance.PLACE_END),
        (locker_instance.KIND_WRITE, locker_instance.PLACE_BEGIN),
        (locker_instance.KIND_WRITE, locker_instance.PLACE_END),
        (locker_instance.KIND_READ, locker_instance.PLACE_BEGIN),
        (locker_instance.KIND_READ, locker_instance.PLACE_END),
        (locker_instance.KIND_WRITE, locker_instance.PLACE_BEGIN),
        (locker_instance.KIND_WRITE, locker_instance.PLACE_END),
    ]


@pytest.mark.parametrize("thread_count", [5, 10, 20])
def test_multiple_reads(locker_instance, thread_count):
    def activity(locker_instance):
        with locker_instance.lock.readlock:
            time.sleep(random.uniform(0.1, 0.01))
            locker_instance.store_log(locker_instance.KIND_READ, locker_instance.PLACE_BEGIN)
            time.sleep(random.uniform(0.1, 0.01))
            locker_instance.store_log(locker_instance.KIND_READ, locker_instance.PLACE_END)
            time.sleep(random.uniform(0.1, 0.01))

    entity_class = locker_instance.entity
    entities = []
    for _ in range(thread_count):
        e = entity_class(target=activity, args=(locker_instance, ))
        entities.append(e)
        e.start()

    for entity in entities:
        entity.join()

    b_count, e_count = 0, 0
    for _, place in locker_instance.output:
        if place == locker_instance.PLACE_BEGIN:
            b_count += 1
        elif place == locker_instance.PLACE_END:
            e_count += 1
        else:
            assert False
        assert b_count >= e_count

    assert b_count == e_count


@pytest.mark.parametrize("thread_count", [5, 10, 20])
def test_multiple_writes(locker_instance, thread_count):
    def activity(locker_instance):
        with locker_instance.lock.writelock:
            time.sleep(random.uniform(0.1, 0.01))
            locker_instance.store_log(locker_instance.KIND_WRITE, locker_instance.PLACE_BEGIN)
            time.sleep(random.uniform(0.1, 0.01))
            locker_instance.store_log(locker_instance.KIND_WRITE, locker_instance.PLACE_END)
            time.sleep(random.uniform(0.1, 0.01))

    entity_class = locker_instance.entity
    entities = []
    for _ in range(thread_count):
        e = entity_class(target=activity, args=(locker_instance, ))
        entities.append(e)
        e.start()

    for entity in entities:
        entity.join()

    assert [
        (locker_instance.KIND_WRITE, locker_instance.PLACE_BEGIN),
        (locker_instance.KIND_WRITE, locker_instance.PLACE_END),
    ] * thread_count == list(locker_instance.output)


@pytest.mark.parametrize(
    "read_thread_count,write_thread_count", [(5, 15), (10, 10), (15, 5)])
def test_multiple_reads_and_writes(locker_instance, read_thread_count, write_thread_count):

    def activity_write(locker_instance):
        with locker_instance.lock.writelock:
            time.sleep(random.uniform(0.1, 0.01))
            locker_instance.store_log(locker_instance.KIND_WRITE, locker_instance.PLACE_BEGIN)
            time.sleep(random.uniform(0.1, 0.01))
            locker_instance.store_log(locker_instance.KIND_WRITE, locker_instance.PLACE_END)
            time.sleep(random.uniform(0.1, 0.01))

    def activity_read(locker_instance):
        with locker_instance.lock.writelock:
            time.sleep(random.uniform(0.1, 0.01))
            locker_instance.store_log(locker_instance.KIND_READ, locker_instance.PLACE_BEGIN)
            time.sleep(random.uniform(0.1, 0.01))
            locker_instance.store_log(locker_instance.KIND_READ, locker_instance.PLACE_END)
            time.sleep(random.uniform(0.1, 0.01))

    entity_class = locker_instance.entity
    entities = []
    for _ in range(read_thread_count):
        e = entity_class(target=activity_read, args=(locker_instance, ))
        entities.append(e)
        e.start()

    for _ in range(write_thread_count):
        e = entity_class(target=activity_write, args=(locker_instance, ))
        entities.append(e)
        e.start()

    for entity in entities:
        entity.join()

    b_count, e_count = 0, 0
    prev_kind, prev_place = None, None
    for kind, place in locker_instance.output:
        if place == locker_instance.PLACE_BEGIN:
            b_count += 1
        elif place == locker_instance.PLACE_END:
            e_count += 1
        else:
            assert False

        if kind == locker_instance.KIND_WRITE and place == locker_instance.PLACE_END:
            assert (prev_kind, prev_place) == (locker_instance.KIND_WRITE, locker_instance.PLACE_BEGIN)

        assert b_count >= e_count
        prev_kind, prev_place = kind, place

    assert b_count == e_count
