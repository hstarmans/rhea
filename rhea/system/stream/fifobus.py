#
# Copyright (c) 2013-2015 Christopher L. Felton
#

from myhdl import Signal, intbv, always_comb


_fb_num = 0
_fb_list = {}


def _add_bus(fb, name=''):
    """ globally keep track of all the buses added.
    """
    global _fb_num, _fb_list
    _fb_num += 1
    _fb_list[name] = fb


class FIFOBus(object):
    def __init__(self, size=16, width=8):
        """ A FIFO interface
        This interface encapsulates the signals required to interface
        to a FIFO.  This object also contains the configuration information
        of a FIFO: word width and the FIFO size (depth).

        Arguments:
            size (int): The depth of the FIFO, the maximum number of
                elements a FIFO can hold.

            width (int): The width of the elements in the FIFO.
        """
        self.name = "fifobus{0}".format(_fb_num)

        # @todo: add write clock and read clock to the interface!
        # @todo: use longer names read, read_valid, read_data,
        # @todo: write, write_data, etc.!

        # all the data signals are from the perspective
        # of the FIFO being interfaced to. That is , write_data
        # means write_to and read_data means read_from      
        self.clear = Signal(bool(0))           # fifo clear
        #self.wclk = None                      # write side clock
        self.write = Signal(bool(0))              # write strobe to fifo
        self.write_data = Signal(intbv(0)[width:])  # fifo data in

        #self.rclk = None                      # read side clock
        self.read = Signal(bool(0))              # fifo read strobe
        self.read_data = Signal(intbv(0)[width:])  # fifo data out
        self.read_valid = Signal(bool(0))
        self.empty = Signal(bool(1))           # fifo empty
        self.full = Signal(bool(0))            # fifo full
        self.count = Signal(intbv(0, min=0, max=size+1))

        self.width = width
        self.size = size

        _add_bus(self, self.name)
        
    def __str__(self):
        s = "wr: {} {:04X}, rd: {} {:04X}, empty {}, full {}".format(
            int(self.write), int(self.write_data), int(self.read), int(self.read_data),
            int(self.empty), int(self.full))
        return s

    def writetrans(self, data):
        """ Do a write transaction
        This generator will drive the FIFOBus signals required to
        perform a write.  If the FIFO is full an exception is thrown.
        """
        if not self.full:
            self.write.next = True
            self.write_data.next = data
            yield self.write_clock.posedge
            self.write.next = False

    def readtrans(self):
        """ Do a read transaction
        This generator will drive the FIFOBus signals required to
        perform a read.  If the FIFO is empty an exception is thrown
        """
        if not self.empty:
            self.read.next = True
            yield self.read_clock.posedge
            self.read.next = False
            while not self.valid:
                yield self.read_clock.posedge
            data = int(self.read_data)

    def assign_read_write_paths(self, readpath, writepath):
        """
        Assign the signals from the `readpath` to the read signals
        of this interface and same for write
        """
        assert isinstance(readpath, FIFOBus)
        assert isinstance(writepath, FIFOBus)
        
        @always_comb
        def beh_assign():
            # read
            readpath.read_data.next = self.read_data
            readpath.empty.next = self.empty
            readpath.read_valid.next = self.read_valid
            
            # write           
            self.write_data.next = writepath.write_data
            self.write.next = writepath.write
            writepath.full.next = self.full
           
        return beh_assign

    # @todo: get the separate buses
    # def get_upstream()    
    #     """ write bus, into the FIFO """
    #
    # def get_downstream()
    #     """ 
