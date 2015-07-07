from spyne.application import Application
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode
from spyne.model.primitive import Boolean
from spyne.model.primitive import DateTime
from spyne.model.complex import Array, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model.complex import ComplexModel

import logging
from datetime import date
import datetime
import time

NS = 'http://soa.cs.uwf.edu/airlineData'

DELAY = 0.5

class Passenger(ComplexModel):
    __namespace__ = NS
    __type_name__ = 'PassengerType'

    dateOfBirth = Unicode
    firstName = Unicode
    lastName = Unicode


class Flight(ComplexModel):
    __namespace__ = NS

    flightId = Unicode
    departAirport = Unicode
    arriveAirport = Unicode
    departTime = DateTime
    arriveTime = DateTime
    flightSeatsAvailable = Integer
    flightSeatPriceUSD = Integer

FlightList = Iterable(Flight)
FlightList.__namespace__ = NS
FlightList.__type_name__ = 'ArrayOfFlight'

class Booking(ComplexModel):
    __namespace__ = NS

    bookingRequestNumber = Integer
    ticketNumber = Integer
    flightId = Unicode
    passenger = Passenger

ps = Iterable(Passenger)
ps.__namespace__ = NS
ps.__type_name__ = 'ArrayOfPassenger'

class PassengerResult(ComplexModel):
    __namespace__ = 'http://soa.cs.uwf.edu/airlineData'
    flight = Flight
    passenger = ps


class AirlineService(ServiceBase):
    __namespace__ = 'http://soa.cs.uwf.edu/airlineData'

    @srpc(Boolean, Integer, Unicode, Passenger, _returns=Booking)
    def bookSeat(isTestOnly, bookingRequestNumber, flightId, passenger):
        global DELAY
        time.sleep(.393)
        return Booking(bookingRequestNumber=bookingRequestNumber,ticketNumber=1,flightId=flightId,passenger=passenger)

    @srpc(Unicode, Unicode, DateTime, DateTime, Integer, Integer, _returns=FlightList)
    def findSeats(departAirport, arriveAirport, earliestDepartTime, latestDepartTime, minimumSeatsAvailable, maximumFlightsToReturn):
        global DELAY
        time.sleep(.370)
        return []

    @srpc(Unicode, _returns=PassengerResult)
    def getPassengerList(flightId):
        global DELAY
        time.sleep(.381)
        f = Flight(flightId=flightId,flightSeatsAvailable=1, departAirport="XXX",arriveAirport="XXX",departTime=datetime.datetime.now(),arriveTime=datetime.datetime.now(),flightSeatPriceUSD=100)
        p = Passenger(dateOfBirth='1900-01-01',firstName='test1',lastName='lastname')
        return PassengerResult(flight=f, passenger=[p])

    @srpc(_returns=Boolean)
    def resetBackend():
        global DELAY
        time.sleep(DELAY)
        return True

application = Application([AirlineService],
    tns='http://soa.cs.uwf.edu/airlineMessage',
    in_protocol=Soap11(),
    out_protocol=Soap11()
)

def make_app():
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    logging.getLogger('spyne.server.wsgi').setLevel(logging.DEBUG)
    
    from wsgiref.simple_server import make_server, WSGIRequestHandler
    wsgi_app = WsgiApplication(application)
    class QuietHandler(WSGIRequestHandler):
        def log_request(*args, **kw): pass

    return make_server('0.0.0.0', 8000, wsgi_app, handler_class=QuietHandler)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)3d %(funcName)20s() -- %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    s = make_app()
    s.serve_forever()
