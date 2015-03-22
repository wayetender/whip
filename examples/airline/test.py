import sys
sys.path.append('../')
import test_utils

from suds.client import Client
import logging
import datetime
import mockairlineserver as server


# host = 'http://54.68.55.200/rrairlines/rrService.php?wsdl'
host = 'http://localhost:8000/?wsdl'

setup_f = test_utils.setup_adapter('adapter.yaml', server.make_app())

logging.getLogger('spyne.protocol.xml').setLevel(logging.INFO)
logging.getLogger('suds').setLevel(logging.INFO)

def run_bookflight():
    global host
    total = test_utils.StopWatch('total')

    client = Client(host, headers={'Content-Type': 'iso-8859-1'})
    client.options.cache.clear()
    tracker = test_utils.track_suds_traffic(client)

    client.service.resetBackend()

    client.service.findSeats('ANY', 'ANY', '2012-01-16T03:01:01.015Z', '2012-01-16T04:01:01.015Z', 1, 10)
    flight = 'RR6051'

    client.service.getPassengerList(flight)

    passenger = client.factory.create('{http://soa.cs.uwf.edu/airlineData}PassengerType')
    
    passenger.dateOfBirth = '1989-01-01'
    n = 1
    bookingNumber = 32
    passenger.firstName = 'test' + str(n)
    passenger.lastName = 'lastName'

    client.service.bookSeat(False, bookingNumber, flight, passenger)

    #asd = client.service.getPassengerList(flight).flight.flightSeatsAvailable

    total.stop()
    return (tracker, total)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)3d %(funcName)20s() -- %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    NUM_TRIALS = 5
    print "starting %d trials..." % NUM_TRIALS
    report = []
    for trial in xrange(NUM_TRIALS):
        setup_f()
        (traffic, stopwatch) = run_bookflight()
        stats = test_utils.get_adapter_stats()
        report.append((traffic, stopwatch, stats))
        test_utils.teardown_adapter()
        print "Trial %d / %d: %s" % (trial+1, NUM_TRIALS, stopwatch)
    print "-- End of %d trials --" % NUM_TRIALS
    print test_utils.format_stats(report)

