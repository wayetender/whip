
ghost Flight {
    @identifier flightId,
    @immutable departTime,
    passengers
} requires {{
  (flightId[0].isLetter() and flightId[1].isLetter() and len(flightId) <= 6) 
}}

ghost BookingRequest {
    @identifier bookingRequestNumber
}


service Airline {
    
    bookSeat(isTestOnly, bookingRequestNumber, flightId, passenger)
    @identifies flight:Flight by {{ flightId }}
    @identifies bookingReq:BookingRequest by {{ bookingRequestNumber }}
    @precondition {{ isFresh(bookingReq) }}
    @updates flight.passengers to {{ 
       # print "passenger is %s" % passenger
        return flight.passengers + [passenger] }}
    @postcondition {{ 
       bookingRequestNumber == result['bookingRequestNumber'] and flightId == result['flightId']
    }}
    @postcondition {{
        passenger['firstName'] == result['passenger']['firstName'] and \
            passenger['lastName'] == result['passenger']['lastName'] and \
            flightId == result['flightId']
    }}
    

    findSeats(departAirport, arriveAirport, earliestDepartTime, latestDepartTime, minimumSeatsAvailable, maximumFlightsToReturn)
    @identifies flights:Flight[] by {{ 
        for flight in result: yield (flight.flightId)
    }}
    @updates {{ 
      for flight in result:
        flightGhost = flights[flight.flightId]
        update(flightGhost, 'departTime', flight['departTime'])
    }}
    @postcondition {{
        if maximumFlightsToReturn < len(result): return False
        for row in result:
            if row['departAirport'] != departAirport and departAirport != 'ANY': return False
            if row['arriveAirport'] != arriveAirport and arriveAirport != 'ANY': return False
            if row['departTime'] < earliestDepartTime or row.departTime > latestDepartTime: return False
            if row['flightSeatsAvailable'] < minimumSeatsAvailable: return False 
        return True
    }}

    getPassengerList(flightId)
    @identifies flight:Flight by {{ flightId }}
    @initializes flight.passengers to {{ 
        #print "blah %s" % result['passenger'] 
        return result['passenger'] 
    }} if {{ isUnknown(flight.passengers) }}
    @postcondition {{ 
        def ghostContains(passenger):
            for p in flight.passengers:
                if p['firstName'] == passenger['firstName'] and p['lastName'] == passenger['lastName']: return True
            return False
            
        #print "p is %s" % flight.passengers
        #print "g is %s" % result['passenger']
        if len(result['passenger']) != len(flight.passengers): return False
        for p in result['passenger']:
            if not ghostContains(p):
                return False
        return True
    }}

    resetBackend()
}
