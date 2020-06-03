from enum import Enum


class AdsConnection(Enum):
    """ADS connection configuration."""
    AMS_NET_ID = "127.0.0.1.1.1"
    AMS_NET_PORT = 851


class Inputs(Enum):
    """Input variables."""
    ILS1 = "MAIN.iLS1"          # light sensor LS1
    ILS2 = "MAIN.iLS2"          # light sensor LS2
    ILS3 = "MAIN.iLS3"          # light sensor LS3
    ILS4 = "MAIN.iLS4"          # light sensor LS4
    IM11 = "MAIN.iM1ylhaalla"   # the barrier 1 is up
    IM12 = "MAIN.iM1alhaalla"   # the barrier 1 is down
    IM21 = "MAIN.iM2ylhaalla"   # the barrier 2 is up
    IM22 = "MAIN.iM2alhaalla"   # the barrier 2 is down
    IS1 = "MAIN.iS1"            # reset the car counter


class Outputs(Enum):
    """Output variables."""
    QM1RAISE = "MAIN.qM1ylos"   # raise the barrier 1
    QM1LOWER = "MAIN.qM1alas"   # lower the barrier 1
    QM2RAISE = "MAIN.qM2ylos"   # raise the barrier 2
    QM2LOWER = "MAIN.qM2alas"   # lower the barrier 2
    QH0 = "MAIN.qH0"            # indicator light
