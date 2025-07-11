#include <iostream>
#include <cstring>

class Reservation {
private:
    char passengerName[50];
    int seatNumber;
    char flightDate[12];
    char originCity[50];
    char destinationCity[50];
    int flightCost;

    static int totalReservations;

    bool checkSeatValidity(int seat) {
        return seat >= 1 && seat <= 50;
    }

    int calculateCost(int paymentOption) {
        int baseCost = 250;
        int cost;

        switch (paymentOption) {
            case 1:
                cost = baseCost - (baseCost * 10 / 100); // 10% discount for EMU students
                break;
            case 2:
                cost = baseCost - (baseCost * 15 / 100); // 15% discount for EMU-IT-MIS students
                break;
            case 3:
                cost = baseCost; // Standard passenger, no discount
                break;
            default:
                cost = 0;
        }

        return cost;
    }

public:
    Reservation() {
        strcpy(passengerName, "");
        seatNumber = 0;
        strcpy(flightDate, "");
        strcpy(originCity, "");
        strcpy(destinationCity, "");
        flightCost = 0;
        totalReservations++;
    }

    ~Reservation() {
        std::cout << "Object destroyed." << std::endl;
    }

    void setPassengerName(const char* name) {
        strcpy(passengerName, name);
    }

    void setSeatNumber(int seat) {
        if (checkSeatValidity(seat)) {
            seatNumber = seat;
            std::cout << "Seat number " << seatNumber << " is reserved for " << passengerName << std::endl;
        } else {
            std::cout << "Seat number is invalid!!! Re-enter seat number: ";
            std::cin >> seat;
            setSeatNumber(seat);
        }
    }

    void setFlightDate(const char* date) {
        strcpy(flightDate, date);
    }

    void setOriginCity(const char* origin) {
        strcpy(originCity, origin);
    }

    void setDestinationCity(const char* destination) {
        strcpy(destinationCity, destination);
    }

    void setPaymentOption(int option) {
        flightCost = calculateCost(option);
    }

    static void showFlight(const Reservation& res) {
        std::cout << res.passengerName << "\t" << res.seatNumber << "\t" << res.flightDate << "\t"
                  << res.originCity << "\t" << res.destinationCity << "\t" << res.flightCost << std::endl;
    }

    static int getTotalReservations() {
        return totalReservations;
    }
};

int Reservation::totalReservations = 0;

int main() {
    Reservation resAuto;
    Reservation* resPtr1 = new Reservation();
    Reservation* resPtr2 = new Reservation();
    Reservation* resArr = new Reservation[10];

    resAuto.setPassengerName("Mario Bruno");

    std::cout << "Automatic Object:" << std::endl;
    Reservation::showFlight(resAuto);

    std::cout << "Pointer Object 1:" << std::endl;
    Reservation::showFlight(*resPtr1);

    std::cout << "Pointer Object 2:" << std::endl;
    Reservation::showFlight(*resPtr2);

    std::cout << "Array Objects:" << std::endl;
    for (int i = 0; i < 10; i++) {
        std::cout << "
