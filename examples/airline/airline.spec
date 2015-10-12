
ghost BookingRequest {
    @identifier bookingRequestNumber
}


service Airline {

    bookSeat(isTestOnly, bookingRequestNumber, flightId, passenger)
    @identifies bookingReq:BookingRequest by {{ bookingRequestNumber }}
    @precondition {{ isFresh(bookingReq) }}
    @precondition {{ ' ' not in passenger['firstName'] }}
    @precondition {{ ' ' not in passenger['lastName'] }}
    @postcondition {{ 
       bookingRequestNumber == result['bookingRequestNumber'] and flightId == result['flightId']
    }}
    @postcondition {{
        passenger['firstName'] == result['passenger']['firstName'] and \
            passenger['lastName'] == result['passenger']['lastName'] and \
            flightId == result['flightId']
    }}
    

    findSeats(departAirport, arriveAirport, earliestDepartTime, latestDepartTime, minimumSeatsAvailable, maximumFlightsToReturn)
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
    

    resetBackend()
}
