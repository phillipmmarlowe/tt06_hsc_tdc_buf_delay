import cocotb
import cocotb.utils as utils
import csv
from cocotb.clock import Clock, Timer
from cocotb.triggers import ClockCycles, Timer, RisingEdge, FallingEdge
from cocotb.decorators import coroutine

# TODO: move elsewhere
class TDCCtrl:
    
    def __init__(self, clk_period, dut, n_sync_stages):
        self.clk_period=clk_period
        self.dut=dut
        self.n_sync_stages=n_sync_stages
        self.clock_launch_coru=None
        self.clock_capt_coru=None
        self.theta_ps=0
        self.n_samples=0
        self.hw_samples= {
            "THETA_PS"   : [],
            "HW_OUT"     : [],
            "HW_OUT_INV" : [],
            "PULSE_POS"  : [],
            "SIM_TIME"   : []
        }
        self.src_ctrl = {
            "PG_IN"  : 0,
            "PG_TOG" : 1 
        }
        self.reg_bypass = {
            "BYPASS" : 1,
            "REG"    : 0
        }
    
    @cocotb.coroutine
    def set_theta_ps(self, theta_ps):
        self.theta_ps=theta_ps
        yield cocotb.start_soon(self.__restart_clks__())
    
    @cocotb.coroutine
    def reset_design(self):
        yield cocotb.start_soon(self.__reset_design__())

    @cocotb.coroutine
    def pg_cfg(self, pg_src="PG_IN", pg_byp="PG_REG"):
        match (pg_src, pg_byp):
            case ("PG_IN", "PG_BYPASS"):
                yield cocotb.start_soon(self.__pg_in_byp_reg__())
            case ("PG_IN", "PG_REG"):
                yield cocotb.start_soon(self.__pg_in_reg__())
            case ("PG_TOG", "PG_BYPASS"):
                yield cocotb.start_soon(self.__pg_tog_byp_reg__())
            case ("PG_TOG", "PG_REG"):
                yield cocotb.start_soon(self.__pg_tog_reg__())

    @cocotb.coroutine
    def get_samples(self, n):
        self.n_samples = n
        yield cocotb.start_soon(self.__get_samples__()) 

    async def __start_clks__(self):    
        # Start launch clk
        self.clock_launch_coru = cocotb.start_soon(Clock(self.dut.clk_launch, period=self.clk_period, units="ns").start())
        await RisingEdge(self.dut.clk_launch)
        # Phase delay capture clk start
        await Timer(self.theta_ps, units='ps')
        # Start capture clk
        self.clock_capt_coru   = cocotb.start_soon(Clock(self.dut.clk_capture, period=self.clk_period, units="ns").start())
        await RisingEdge(self.dut.clk_capture)
        # Now safe to deassert reset, future phase-shifts can keep reset deasserted
        self.dut.rst_n.value = 1
    
    async def __restart_clks__(self):
        if(self.clock_launch_coru != None):
            await RisingEdge(self.dut.clk_launch)
            self.clock_launch_coru.kill()
        if(self.clock_capt_coru != None):
            await RisingEdge(self.dut.clk_capture)
            self.clock_capt_coru.kill()
        self.clock_launch_coru = None
        self.clock_capt_coru = None
        start_clocks_thread = cocotb.start_soon(self.__start_clks__())
        await start_clocks_thread

    async def __reset_design__(self):
        self.dut.ena.value = 1
        self.dut.rst_n.value = 0
    
    async def __pg_in_byp_reg__(self):
        self.dut.pg_src.value = self.src_ctrl["PG_IN"]
        self.dut.pg_bypass.value = self.reg_bypass["BYPASS"]
    
    async def __pg_in_reg__(self):
        self.dut.pg_src.value = self.src_ctrl["PG_IN"]
        self.dut.pg_bypass.value = self.reg_bypass["REG"]

    async def __pg_tog_byp_reg__(self):
        self.dut.pg_src.value = self.src_ctrl["PG_TOG"]
        self.dut.pg_bypass.value = self.reg_bypass["BYPASS"]

    async def __pg_tog_reg__(self):
        self.dut.pg_src.value = self.src_ctrl["PG_TOG"]
        self.dut.pg_bypass.value = self.reg_bypass["REG"]

    async def __get_samples__(self):
        '''
        If the pg is toggling and clocks are active, collect n traces
        '''
        if(self.dut.pg_src.value == self.src_ctrl["PG_TOG"]):
            if(self.clock_launch_coru != None and self.clock_capt_coru != None):
                for i in range(self.n_samples):
                    hws = []
                    hws_inv =[]
                    sim_times = []
                    pulse_positions = ["FALL", "SAT_FALL", "RISE", "SAT_RISE"]            
                    self.hw_samples["THETA_PS"].append(self.theta_ps)
                    # Wait for a rising edge of the toggle input
                    await RisingEdge(self.dut.pg_tog)
                    # Depending on setting, wait for input propagation
                    if(self.dut.pg_bypass.value == self.reg_bypass["REG"]):
                        await RisingEdge(self.dut.clk_launch)
                    # Wait for delay line output propagation
                    # +2 - +1 HW delay output stage, +1 sampling immediately @posedge
                    for wait_clk in range(self.n_sync_stages + 2):
                        await RisingEdge(self.dut.clk_capture)
                    # Get two sample groups
                    for sample in range(4):                
                        # Resample each cycle
                        await RisingEdge(self.dut.clk_capture)
                        time_step = utils.get_sim_time(units='step')
                        # Sample hw
                        try:
                            hw = int(self.dut.hw.value)
                            hws.append(hw)
                            hws_inv.append(64-hw)
                            sim_times.append(time_step)
                        except:
                            hws.append("x")
                            hws_inv.append("x")
                            sim_times.append(time_step)
                    # Collect data
                    self.hw_samples["PULSE_POS"] = self.hw_samples["PULSE_POS"] + pulse_positions
                    self.hw_samples["HW_OUT"]  =  self.hw_samples["HW_OUT"] + hws
                    self.hw_samples["HW_OUT_INV"] = self.hw_samples["HW_OUT_INV"] + hws_inv
                    self.hw_samples["SIM_TIME"] = self.hw_samples["SIM_TIME"] + sim_times
                    await RisingEdge(self.dut.clk_launch)
        await RisingEdge(self.dut.clk_launch) 

@cocotb.test()
async def test_tdc(dut):
    dut._log.info("Start")
    f_clk_ns = 54
    # 1 for output of TDC, 1 for output of thermometer to HW encoder
    output_sync_stages = 1
    tdc_ctrl = TDCCtrl(clk_period=f_clk_ns, dut=dut, n_sync_stages=output_sync_stages)
    pg_cfg_thread = cocotb.start_soon(tdc_ctrl.pg_cfg("PG_TOG", "PG_BYPASS"))
    await pg_cfg_thread
    reset_thread = cocotb.start_soon(tdc_ctrl.reset_design())
    await reset_thread
    for theta_ps in range(0, 2*f_clk_ns*1000+1, 10):
        set_theta_thread = cocotb.start_soon(tdc_ctrl.set_theta_ps(theta_ps))
        await set_theta_thread
        get_samples_thread = cocotb.start_soon(tdc_ctrl.get_samples(1))
        await get_samples_thread
    # Writing to CSV to avoid use of Pandas (not included in TT venv)
    with open('./theta_sweep.csv', 'w', newline='') as f_output:
        csv_output = csv.writer(f_output)
        csv_output.writerow(tdc_ctrl.hw_samples.keys())
        csv_output.writerows([*zip(*tdc_ctrl.hw_samples.values())])
    
