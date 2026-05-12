import pyromat as pm
import random
from abc import ABC, abstractmethod

# Configure Pyromat to use convenient standard units
pm.config["unit_pressure"] = "kPa"
pm.config["unit_temperature"] = "C"
pm.config["unit_matter"] = "kg"
pm.config["unit_energy"] = "kJ"

# Initialize water/steam object
steam = pm.get("mp.H2O")


class RankineCycle(ABC):
    """Abstract base class for Rankine cycle problems."""
    
    def __init__(self):
        self.p_high = None
        self.p_low = None
        self.t_high = None
        self.problem_statement = ""
        self.solution = ""
    
    def generate_parameters(self):
        """Generate random cycle parameters. Override in subclasses."""
        self.p_high = random.randint(6, 15) * 1000
        self.p_low = random.randint(5, 100)
        self.t_high = random.randrange(400, 551, 50)
    
    @abstractmethod
    def calculate(self):
        """Perform thermodynamic calculations. Must be implemented by subclasses."""
        pass
    
    def get_problem_statement(self):
        """Return the formatted problem statement."""
        return self.problem_statement
    
    def get_solution(self):
        """Return the formatted solution."""
        return self.solution


class SimpleRankineCycle(RankineCycle):
    """Simple Rankine cycle implementation."""
    
    def generate_parameters(self):
        self.p_high = random.randint(5, 15) * 1000
        self.p_low = random.randint(5, 100)
        self.t_high = random.randrange(400, 551, 50)
    
    def calculate(self):
        self.generate_parameters()
        
        self.problem_statement = (
            f"--- PROBLEM (Simple Rankine Cycle) ---\n"
            f"Consider a simple ideal Rankine cycle with water as the working fluid. "
            f"Steam enters the turbine at {self.p_high} kPa and {self.t_high} °C and is "
            f"condensed in the condenser at a pressure of {self.p_low} kPa. "
            f"Calculate the net work output (kJ/kg), heat added (kJ/kg), and the thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_low, x=0)[0]
        v1 = steam.v(p=self.p_low, x=0)[0]
        
        w_pump = v1 * (self.p_high - self.p_low)
        h2 = h1 + w_pump
        
        h3 = steam.h(p=self.p_high, T=self.t_high)[0]
        s3 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h4 = steam.h(p=self.p_low, s=s3)[0]
        
        w_turb = h3 - h4
        w_net = w_turb - w_pump
        q_in = h3 - h2
        eta = (w_net / q_in) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Pump In):  h1 = {h1:.2f} kJ/kg, v1 = {v1:.6f} m^3/kg\n"
            f"State 2 (Pump Out): h2 = {h2:.2f} kJ/kg (w_pump = {w_pump:.2f} kJ/kg)\n"
            f"State 3 (Turb In):  h3 = {h3:.2f} kJ/kg, s3 = {s3:.4f} kJ/kg-K\n"
            f"State 4 (Turb Out): h4 = {h4:.2f} kJ/kg\n\n"
            f"Net Work Output: {w_net:.2f} kJ/kg\n"
            f"Heat Added (Qin): {q_in:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )


class ReheatRankineCycle(RankineCycle):
    """Reheat Rankine cycle implementation."""
    
    def __init__(self, num_reheats=None):
        super().__init__()
        self.num_reheats = num_reheats or random.randint(1, 2)
    
    def generate_parameters(self):
        self.p_high = random.randint(8, 15) * 1000
        self.p_low = random.randint(5, 50)
        self.t_high = random.randrange(450, 551, 50)
    
    def calculate(self):
        self.generate_parameters()
        
        if self.num_reheats == 1:
            self._calculate_one_reheat()
        else:
            self._calculate_two_reheats()
    
    def _calculate_one_reheat(self):
        p_reheat = random.randint(1000, 3000)
        t_reheat = random.randint(400, self.t_high)
        
        self.problem_statement = (
            f"--- PROBLEM (Ideal Reheat Rankine Cycle with 1 Reheat) ---\n"
            f"Steam enters the high-pressure turbine of an ideal reheat Rankine cycle "
            f"at {self.p_high} kPa and {self.t_high} °C. It is then extracted at {p_reheat} kPa "
            f"and reheated to {t_reheat} °C. The steam expands in the low-pressure turbine "
            f"to a condenser pressure of {self.p_low} kPa. "
            f"Calculate the net work output (kJ/kg) and the thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_low, x=0)[0]
        v1 = steam.v(p=self.p_low, x=0)[0]
        w_pump = v1 * (self.p_high - self.p_low)
        h2 = h1 + w_pump
        
        h3 = steam.h(p=self.p_high, T=self.t_high)[0]
        s3 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h4 = steam.h(p=p_reheat, s=s3)[0]
        h5 = steam.h(p=p_reheat, T=t_reheat)[0]
        s5 = steam.s(p=p_reheat, T=t_reheat)[0]
        h6 = steam.h(p=self.p_low, s=s5)[0]
        
        w_turb_hp = h3 - h4
        w_turb_lp = h5 - h6
        w_turb_total = w_turb_hp + w_turb_lp
        w_net = w_turb_total - w_pump
        q_primary = h3 - h2
        q_reheat = h5 - h4
        q_in_total = q_primary + q_reheat
        eta = (w_net / q_in_total) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Pump In):    h1 = {h1:.2f} kJ/kg\n"
            f"State 2 (Pump Out):   h2 = {h2:.2f} kJ/kg\n"
            f"State 3 (HP Turb In): h3 = {h3:.2f} kJ/kg, s3 = {s3:.4f} kJ/kg-K\n"
            f"State 4 (HP Turb Out):h4 = {h4:.2f} kJ/kg\n"
            f"State 5 (LP Turb In): h5 = {h5:.2f} kJ/kg, s5 = {s5:.4f} kJ/kg-K\n"
            f"State 6 (LP Turb Out):h6 = {h6:.2f} kJ/kg\n\n"
            f"Total Turbine Work: {w_turb_total:.2f} kJ/kg\n"
            f"Total Heat Added: {q_in_total:.2f} kJ/kg\n"
            f"Net Work Output: {w_net:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )
    
    def _calculate_two_reheats(self):
        p_reheat1 = random.randint(3000, 6000)
        p_reheat2 = random.randint(500, 2000)
        t_reheat1 = random.randint(400, self.t_high)
        t_reheat2 = random.randint(400, self.t_high)
        
        self.problem_statement = (
            f"--- PROBLEM (Ideal Reheat Rankine Cycle with 2 Reheats) ---\n"
            f"Steam enters the high-pressure turbine of an ideal reheat Rankine cycle "
            f"at {self.p_high} kPa and {self.t_high} °C. It is extracted at {p_reheat1} kPa "
            f"and reheated to {t_reheat1} °C, then expands in the intermediate-pressure turbine. "
            f"It is extracted again at {p_reheat2} kPa and reheated to {t_reheat2} °C, "
            f"expanding in the low-pressure turbine to a condenser pressure of {self.p_low} kPa. "
            f"Calculate the net work output (kJ/kg) and the thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_low, x=0)[0]
        v1 = steam.v(p=self.p_low, x=0)[0]
        w_pump = v1 * (self.p_high - self.p_low)
        h2 = h1 + w_pump
        
        h3 = steam.h(p=self.p_high, T=self.t_high)[0]
        s3 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h4 = steam.h(p=p_reheat1, s=s3)[0]
        h5 = steam.h(p=p_reheat1, T=t_reheat1)[0]
        s5 = steam.s(p=p_reheat1, T=t_reheat1)[0]
        
        h6 = steam.h(p=p_reheat2, s=s5)[0]
        h7 = steam.h(p=p_reheat2, T=t_reheat2)[0]
        s7 = steam.s(p=p_reheat2, T=t_reheat2)[0]
        h8 = steam.h(p=self.p_low, s=s7)[0]
        
        w_turb_hp = h3 - h4
        w_turb_ip = h5 - h6
        w_turb_lp = h7 - h8
        w_turb_total = w_turb_hp + w_turb_ip + w_turb_lp
        w_net = w_turb_total - w_pump
        
        q_primary = h3 - h2
        q_reheat1 = h5 - h4
        q_reheat2 = h7 - h6
        q_in_total = q_primary + q_reheat1 + q_reheat2
        eta = (w_net / q_in_total) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Pump In):    h1 = {h1:.2f} kJ/kg\n"
            f"State 2 (Pump Out):   h2 = {h2:.2f} kJ/kg\n"
            f"State 3 (HP Turb In): h3 = {h3:.2f} kJ/kg\n"
            f"State 4 (HP Turb Out):h4 = {h4:.2f} kJ/kg\n"
            f"State 5 (IP Turb In): h5 = {h5:.2f} kJ/kg\n"
            f"State 6 (IP Turb Out):h6 = {h6:.2f} kJ/kg\n"
            f"State 7 (LP Turb In): h7 = {h7:.2f} kJ/kg\n"
            f"State 8 (LP Turb Out):h8 = {h8:.2f} kJ/kg\n\n"
            f"Total Turbine Work: {w_turb_total:.2f} kJ/kg\n"
            f"Total Heat Added: {q_in_total:.2f} kJ/kg\n"
            f"Net Work Output: {w_net:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )


class RegenerativeRankineCycle(RankineCycle):
    """Regenerative Rankine cycle implementation."""
    
    def __init__(self, num_fwh=None):
        super().__init__()
        self.num_fwh = num_fwh or random.randint(1, 2)
    
    def generate_parameters(self):
        self.p_high = random.randint(6, 12) * 1000
        self.p_low = random.randint(5, 50)
        self.t_high = random.randrange(400, 551, 50)
    
    def calculate(self):
        self.generate_parameters()

        if self.num_fwh == 1:
            self._calculate_one_fwh()
        else:
            self._calculate_two_fwh()
    
    def _calculate_one_fwh(self):
        p_ext = random.randint(5, 16) * 100
        
        self.problem_statement = (
            f"--- PROBLEM (Ideal Regenerative Rankine Cycle with 1 OFWH) ---\n"
            f"An ideal regenerative Rankine cycle with an open feedwater heater (OFWH) uses water. "
            f"Steam enters the turbine at {self.p_high} kPa and {self.t_high} °C and expands to a "
            f"condenser pressure of {self.p_low} kPa. Some steam is extracted from the turbine at "
            f"{p_ext} kPa and routed to the OFWH. "
            f"Calculate the extraction fraction (y) and the thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_low, x=0)[0]
        v1 = steam.v(p=self.p_low, x=0)[0]
        w_pump1 = v1 * (p_ext - self.p_low)
        h2 = h1 + w_pump1
        
        h3 = steam.h(p=p_ext, x=0)[0]
        v3 = steam.v(p=p_ext, x=0)[0]
        w_pump2 = v3 * (self.p_high - p_ext)
        h4 = h3 + w_pump2
        
        h5 = steam.h(p=self.p_high, T=self.t_high)[0]
        s5 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h6 = steam.h(p=p_ext, s=s5)[0]
        h7 = steam.h(p=self.p_low, s=s5)[0]
        
        y = (h3 - h2) / (h6 - h2)
        
        w_turb = (h5 - h6) + (1 - y) * (h6 - h7)
        w_pump_total = (1 - y) * w_pump1 + w_pump2
        w_net = w_turb - w_pump_total
        q_in = h5 - h4
        eta = (w_net / q_in) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Pump 1 In):  h1 = {h1:.2f} kJ/kg\n"
            f"State 2 (Pump 1 Out): h2 = {h2:.2f} kJ/kg\n"
            f"State 3 (OFWH Out):   h3 = {h3:.2f} kJ/kg\n"
            f"State 4 (Pump 2 Out): h4 = {h4:.2f} kJ/kg\n"
            f"State 5 (Turb In):    h5 = {h5:.2f} kJ/kg, s5 = {s5:.4f} kJ/kg-K\n"
            f"State 6 (Extraction): h6 = {h6:.2f} kJ/kg\n"
            f"State 7 (Turb Out):   h7 = {h7:.2f} kJ/kg\n\n"
            f"Extraction Fraction (y): {y:.4f} kg_extracted/kg_total\n"
            f"Total Turbine Work: {w_turb:.2f} kJ/kg\n"
            f"Total Pump Work: {w_pump_total:.2f} kJ/kg\n"
            f"Heat Added (Qin): {q_in:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )
    
    def _calculate_two_fwh(self):
        p_ext1 = random.randint(2000, 4000)
        p_ext2 = random.randint(200, 1000)
        
        self.problem_statement = (
            f"--- PROBLEM (Ideal Regenerative Rankine Cycle with 2 OFWHs) ---\n"
            f"An ideal regenerative Rankine cycle with two open feedwater heaters (OFWH) uses water. "
            f"Steam enters the turbine at {self.p_high} kPa and {self.t_high} °C and expands to a "
            f"condenser pressure of {self.p_low} kPa. Steam is extracted from the turbine at "
            f"{p_ext1} kPa for the high-pressure OFWH and at {p_ext2} kPa for the low-pressure OFWH. "
            f"Calculate the extraction fractions (y, z) and the thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_low, x=0)[0]
        v1 = steam.v(p=self.p_low, x=0)[0]
        w_pump1 = v1 * (p_ext2 - self.p_low)
        h2 = h1 + w_pump1
        
        h3 = steam.h(p=p_ext2, x=0)[0]
        v3 = steam.v(p=p_ext2, x=0)[0]
        w_pump2 = v3 * (p_ext1 - p_ext2)
        h4 = h3 + w_pump2
        
        h5 = steam.h(p=p_ext1, x=0)[0]
        v5 = steam.v(p=p_ext1, x=0)[0]
        w_pump3 = v5 * (self.p_high - p_ext1)
        h6 = h5 + w_pump3
        
        h7 = steam.h(p=self.p_high, T=self.t_high)[0]
        s7 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h8 = steam.h(p=p_ext1, s=s7)[0]
        h9 = steam.h(p=p_ext2, s=s7)[0]
        h10 = steam.h(p=self.p_low, s=s7)[0]
        
        y = (h5 - h4) / (h8 - h4)
        z = ((1 - y) * (h3 - h2)) / (h9 - h2)
        
        w_turb = (h7 - h8) + (1 - y) * (h8 - h9) + (1 - y - z) * (h9 - h10)
        w_pump_total = (1 - y - z) * w_pump1 + (1 - y) * w_pump2 + w_pump3
        w_net = w_turb - w_pump_total
        q_in = h7 - h6
        eta = (w_net / q_in) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Pump 1 In):  h1 = {h1:.2f} kJ/kg\n"
            f"State 2 (Pump 1 Out): h2 = {h2:.2f} kJ/kg\n"
            f"State 3 (LP OFWH Out):h3 = {h3:.2f} kJ/kg\n"
            f"State 4 (Pump 2 Out): h4 = {h4:.2f} kJ/kg\n"
            f"State 5 (HP OFWH Out):h5 = {h5:.2f} kJ/kg\n"
            f"State 6 (Pump 3 Out): h6 = {h6:.2f} kJ/kg\n"
            f"State 7 (Turb In):    h7 = {h7:.2f} kJ/kg\n"
            f"State 8 (Ext 1):      h8 = {h8:.2f} kJ/kg\n"
            f"State 9 (Ext 2):      h9 = {h9:.2f} kJ/kg\n"
            f"State 10 (Turb Out):  h10 = {h10:.2f} kJ/kg\n\n"
            f"Extraction Fractions: y = {y:.4f}, z = {z:.4f}\n"
            f"Total Turbine Work: {w_turb:.2f} kJ/kg\n"
            f"Total Pump Work: {w_pump_total:.2f} kJ/kg\n"
            f"Heat Added (Qin): {q_in:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )


class RegenerativeReheatRankineCycle(RankineCycle):
    """Regenerative-Reheat Rankine cycle implementation."""
    
    def __init__(self, case_num=None):
        super().__init__()
        self.case_num = case_num or random.randint(1, 4)
    
    def generate_parameters(self):
        self.p_high = random.randint(8, 15) * 1000
        self.p_low = random.randrange(5, 51, 5)
        self.t_high = random.randrange(450, 551, 20)
        self.t_reheat = random.randrange(400, self.t_high + 1, 20)
    
    def calculate(self):
        self.generate_parameters()
        
        if self.case_num == 1:
            self._calculate_case_1()
        elif self.case_num == 2:
            self._calculate_case_2()
        elif self.case_num == 3:
            self._calculate_case_3()
        else:
            self._calculate_case_4()
    
    def _calculate_case_1(self):
        p_ext = random.randrange(2000, 4001, 50)
        p_reheat_extract = random.randrange(500, 1501, 10)
        
        self.problem_statement = (
            f"--- PROBLEM (Regenerative-Reheat Rankine Cycle - Case 1) ---\n"
            f"An ideal regenerative-reheat Rankine cycle uses water. Steam enters the turbine at "
            f"{self.p_high} kPa and {self.t_high} °C. Steam is extracted at {p_ext} kPa for feedwater heating. "
            f"The remaining steam expands in the turbine, is reheated to {self.t_reheat} °C at {p_reheat_extract} kPa, "
            f"and then expands to the condenser at {self.p_low} kPa. "
            f"Calculate the extraction fraction and thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_high, T=self.t_high)[0]
        s1 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h2 = steam.h(p=p_ext, s=s1)[0]
        h3 = steam.h(p=p_reheat_extract, s=s1)[0]
        
        h4 = steam.h(p=p_reheat_extract, T=self.t_reheat)[0]
        s4 = steam.s(p=p_reheat_extract, T=self.t_reheat)[0]
        
        h5 = steam.h(p=self.p_low, s=s4)[0]
        h6 = steam.h(p=self.p_low, x=0)[0]
        v6 = steam.v(p=self.p_low, x=0)[0]
        w_pump1 = v6 * (p_ext - self.p_low)
        h7 = h6 + w_pump1
        
        h8 = steam.h(p=p_ext, x=0)[0]
        v8 = steam.v(p=p_ext, x=0)[0]
        w_pump2 = v8 * (self.p_high - p_ext)
        h9 = h8 + w_pump2
        
        y = (h8 - h7) / (h2 - h7)
        
        w_turb = (h1 - h2) + (1 - y) * (h3 - h5)
        w_pump_total = (1 - y) * w_pump1 + w_pump2
        w_net = w_turb - w_pump_total
        q_in = (h1 - h9) + (1 - y) * (h4 - h3)
        eta = (w_net / q_in) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Turb In):       h1 = {h1:.2f} kJ/kg, s1 = {s1:.4f} kJ/kg-K\n"
            f"State 2 (Extraction):    h2 = {h2:.2f} kJ/kg\n"
            f"State 3 (Before Reheat): h3 = {h3:.2f} kJ/kg\n"
            f"State 4 (After Reheat):  h4 = {h4:.2f} kJ/kg, s4 = {s4:.4f} kJ/kg-K\n"
            f"State 5 (Turb Out):      h5 = {h5:.2f} kJ/kg\n"
            f"State 6 (Pump 1 In):     h6 = {h6:.2f} kJ/kg\n"
            f"State 7 (Pump 1 Out):    h7 = {h7:.2f} kJ/kg\n"
            f"State 8 (OFWH Out):      h8 = {h8:.2f} kJ/kg\n"
            f"State 9 (Pump 2 Out):    h9 = {h9:.2f} kJ/kg\n\n"
            f"Extraction Fraction (y): {y:.4f} kg_extracted/kg_total\n"
            f"Total Turbine Work: {w_turb:.2f} kJ/kg\n"
            f"Total Pump Work: {w_pump_total:.2f} kJ/kg\n"
            f"Total Heat Added: {q_in:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )
    
    def _calculate_case_2(self):
        p_ext1 = random.randrange(3000, 5001, 100)
        p_after_first = random.randrange(1500, 2501, 50)
        p_ext2 = random.randrange(1000, 2001, 50)
        p_ext3 = random.randrange(200, 801, 10)
        self.t_reheat -= 100
        
        self.problem_statement = (
            f"--- PROBLEM (Regenerative-Reheat Rankine Cycle - Case 2) ---\n"
            f"An ideal regenerative-reheat Rankine cycle uses water. Steam enters at "
            f"{self.p_high} kPa and {self.t_high} °C. Steam is extracted at {p_ext1} kPa, expands to {p_after_first} kPa, "
            f"and is reheated to {self.t_reheat} °C. The steam then expands with extraction points at "
            f"{p_ext2} kPa and {p_ext3} kPa for feedwater heating, finally condensing at {self.p_low} kPa. "
            f"Calculate extraction fractions and thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_high, T=self.t_high)[0]
        s1 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h2 = steam.h(p=p_ext1, s=s1)[0]
        h3 = steam.h(p=p_after_first, s=s1)[0]
        
        h4 = steam.h(p=p_after_first, T=self.t_reheat)[0]
        s4 = steam.s(p=p_after_first, T=self.t_reheat)[0]
        
        h5 = steam.h(p=p_ext2, s=s4)[0]
        h6 = steam.h(p=p_ext3, s=s4)[0]
        h7 = steam.h(p=self.p_low, s=s4)[0]
        
        h8 = steam.h(p=self.p_low, x=0)[0]
        v8 = steam.v(p=self.p_low, x=0)[0]
        w_pump1 = v8 * (p_ext3 - self.p_low)
        h9 = h8 + w_pump1
        
        h10 = steam.h(p=p_ext3, x=0)[0]
        v10 = steam.v(p=p_ext3, x=0)[0]
        w_pump2 = v10 * (p_ext2 - p_ext3)
        h11 = h10 + w_pump2
        
        h12 = steam.h(p=p_ext2, x=0)[0]
        v12 = steam.v(p=p_ext2, x=0)[0]
        w_pump3 = v12 * (p_ext1 - p_ext2)
        h13 = h12 + w_pump3
        
        h14 = steam.h(p=p_ext1, x=0)[0]
        v14 = steam.v(p=p_ext1, x=0)[0]
        w_pump4 = v14 * (self.p_high - p_ext1)
        h15 = h14 + w_pump4
        
        y = (h14 - h13) / (h2 - h13)
        z = ((1 - y) * (h12 - h11)) / (h5 - h11)
        w = ((1 - y - z) * (h10 - h9)) / (h6 - h9)
        
        w_turb = (h1 - h2) + (1 - y) * (h3 - h5) + (1 - y - z) * (h5 - h6) + (1 - y - z - w) * (h6 - h7)
        w_pump_total = (1 - y - z - w) * w_pump1 + (1 - y - z) * w_pump2 + (1 - y) * w_pump3 + w_pump4
        w_net = w_turb - w_pump_total
        q_in = (h1 - h15) + (1 - y) * (h4 - h3)
        eta = (w_net / q_in) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Turb In):       h1 = {h1:.2f} kJ/kg, s1 = {s1:.4f} kJ/kg-K\n"
            f"State 2 (Ext 1):         h2 = {h2:.2f} kJ/kg\n"
            f"State 3 (Before Reheat): h3 = {h3:.2f} kJ/kg\n"
            f"State 4 (After Reheat):  h4 = {h4:.2f} kJ/kg, s4 = {s4:.4f} kJ/kg-K\n"
            f"State 5 (Ext 2):         h5 = {h5:.2f} kJ/kg\n"
            f"State 6 (Ext 3):         h6 = {h6:.2f} kJ/kg\n"
            f"State 7 (Turb Out):      h7 = {h7:.2f} kJ/kg\n"
            f"State 8 (Pump 1 In):     h8 = {h8:.2f} kJ/kg\n"
            f"State 9 (Pump 1 Out):    h9 = {h9:.2f} kJ/kg\n"
            f"State 10 (Pump 2 In):    h10 = {h10:.2f} kJ/kg\n"
            f"State 11 (Pump 2 Out):   h11 = {h11:.2f} kJ/kg\n"
            f"State 12 (Pump 3 In):    h12 = {h12:.2f} kJ/kg\n"
            f"State 13 (Pump 3 Out):   h13 = {h13:.2f} kJ/kg\n"
            f"State 14 (Pump 4 In):    h14 = {h14:.2f} kJ/kg\n"
            f"State 15 (Pump 4 Out):   h15 = {h15:.2f} kJ/kg\n\n"
            f"Extraction Fractions: y = {y:.4f}, z = {z:.4f}, w = {w:.4f}\n"
            f"Total Turbine Work: {w_turb:.2f} kJ/kg\n"
            f"Total Pump Work: {w_pump_total:.2f} kJ/kg\n"
            f"Total Heat Added: {q_in:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )
    
    def _calculate_case_3(self):
        p_first_expand = random.randrange(2000, 4000, 50)
        p_ext1 = random.randrange(1000, 2000, 50)
        p_ext2 = random.randrange(200, 800, 10)
        
        self.problem_statement = (
            f"--- PROBLEM (Regenerative-Reheat Rankine Cycle - Case 3) ---\n"
            f"An ideal regenerative-reheat Rankine cycle uses water. Steam enters at "
            f"{self.p_high} kPa and {self.t_high} °C, expands in the turbine to {p_first_expand} kPa, "
            f"and is reheated to {self.t_reheat} °C. After reheating, the steam expands with "
            f"extraction points at {p_ext1} kPa and {p_ext2} kPa for feedwater heating, "
            f"finally condensing at {self.p_low} kPa. "
            f"Calculate extraction fractions and thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_high, T=self.t_high)[0]
        s1 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h2 = steam.h(p=p_first_expand, s=s1)[0]
        
        h3 = steam.h(p=p_first_expand, T=self.t_reheat)[0]
        s3 = steam.s(p=p_first_expand, T=self.t_reheat)[0]
        
        h4 = steam.h(p=p_ext1, s=s3)[0]
        h5 = steam.h(p=p_ext2, s=s3)[0]
        h6 = steam.h(p=self.p_low, s=s3)[0]
        
        h7 = steam.h(p=self.p_low, x=0)[0]
        v7 = steam.v(p=self.p_low, x=0)[0]
        w_pump1 = v7 * (p_ext2 - self.p_low)
        h8 = h7 + w_pump1
        
        h9 = steam.h(p=p_ext2, x=0)[0]
        v9 = steam.v(p=p_ext2, x=0)[0]
        w_pump2 = v9 * (p_ext1 - p_ext2)
        h10 = h9 + w_pump2
        
        h11 = steam.h(p=p_ext1, x=0)[0]
        v11 = steam.v(p=p_ext1, x=0)[0]
        w_pump3 = v11 * (p_first_expand - p_ext1)
        h12 = h11 + w_pump3
        
        h13 = steam.h(p=p_first_expand, x=0)[0]
        v13 = steam.v(p=p_first_expand, x=0)[0]
        w_pump4 = v13 * (self.p_high - p_first_expand)
        h14 = h13 + w_pump4
        
        y = (h11 - h10) / (h4 - h10)
        z = ((1 - y) * (h9 - h8)) / (h5 - h8)
        
        w_turb = (h1 - h2) + (h3 - h4) + (1 - y) * (h4 - h5) + (1 - y - z) * (h5 - h6)
        w_pump_total = (1 - y - z) * w_pump1 + (1 - y) * w_pump2 + w_pump3 + w_pump4
        w_net = w_turb - w_pump_total
        q_in = (h1 - h14) + (h3 - h2)
        eta = (w_net / q_in) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Turb In):       h1 = {h1:.2f} kJ/kg, s1 = {s1:.4f} kJ/kg-K\n"
            f"State 2 (Before Reheat): h2 = {h2:.2f} kJ/kg\n"
            f"State 3 (After Reheat):  h3 = {h3:.2f} kJ/kg, s3 = {s3:.4f} kJ/kg-K\n"
            f"State 4 (Ext 1):         h4 = {h4:.2f} kJ/kg\n"
            f"State 5 (Ext 2):         h5 = {h5:.2f} kJ/kg\n"
            f"State 6 (Turb Out):      h6 = {h6:.2f} kJ/kg\n"
            f"State 7 (Pump 1 In):     h7 = {h7:.2f} kJ/kg\n"
            f"State 8 (Pump 1 Out):    h8 = {h8:.2f} kJ/kg\n"
            f"State 9 (Pump 2 In):     h9 = {h9:.2f} kJ/kg\n"
            f"State 10 (Pump 2 Out):   h10 = {h10:.2f} kJ/kg\n"
            f"State 11 (Pump 3 In):    h11 = {h11:.2f} kJ/kg\n"
            f"State 12 (Pump 3 Out):   h12 = {h12:.2f} kJ/kg\n"
            f"State 13 (Pump 4 In):    h13 = {h13:.2f} kJ/kg\n"
            f"State 14 (Pump 4 Out):   h14 = {h14:.2f} kJ/kg\n\n"
            f"Extraction Fractions: y = {y:.4f}, z = {z:.4f}\n"
            f"Total Turbine Work: {w_turb:.2f} kJ/kg\n"
            f"Total Pump Work: {w_pump_total:.2f} kJ/kg\n"
            f"Total Heat Added: {q_in:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )
    
    def _calculate_case_4(self):
        p_ext_reheat = random.randrange(2000, 4001, 50)
        p_ext_after = random.randrange(500, 1501, 50)
        
        self.problem_statement = (
            f"--- PROBLEM (Regenerative-Reheat Rankine Cycle - Case 4) ---\n"
            f"An ideal regenerative-reheat Rankine cycle uses water. Steam enters at "
            f"{self.p_high} kPa and {self.t_high} °C and expands in the turbine. Steam is extracted at "
            f"{p_ext_reheat} kPa for feedwater heating and reheating (same pressure). "
            f"The reheated steam expands further with another extraction at {p_ext_after} kPa "
            f"for additional feedwater heating, finally condensing at {self.p_low} kPa. "
            f"Calculate extraction fractions and thermal efficiency."
        )
        
        h1 = steam.h(p=self.p_high, T=self.t_high)[0]
        s1 = steam.s(p=self.p_high, T=self.t_high)[0]
        
        h2 = steam.h(p=p_ext_reheat, s=s1)[0]
        
        h3 = steam.h(p=p_ext_reheat, T=self.t_reheat)[0]
        s3 = steam.s(p=p_ext_reheat, T=self.t_reheat)[0]
        
        h4 = steam.h(p=p_ext_after, s=s3)[0]
        h5 = steam.h(p=self.p_low, s=s3)[0]
        
        h6 = steam.h(p=self.p_low, x=0)[0]
        v6 = steam.v(p=self.p_low, x=0)[0]
        w_pump1 = v6 * (p_ext_after - self.p_low)
        h7 = h6 + w_pump1
        
        h8 = steam.h(p=p_ext_after, x=0)[0]
        v8 = steam.v(p=p_ext_after, x=0)[0]
        w_pump2 = v8 * (p_ext_reheat - p_ext_after)
        h9 = h8 + w_pump2
        
        h10 = steam.h(p=p_ext_reheat, x=0)[0]
        v10 = steam.v(p=p_ext_reheat, x=0)[0]
        w_pump3 = v10 * (self.p_high - p_ext_reheat)
        h11 = h10 + w_pump3
        
        y = (h10 - h9) / (h2 - h9)
        z = ((1 - y) * (h8 - h7)) / (h4 - h7)
        
        w_turb = (h1 - h2) + (h3 - h4) + (1 - y - z) * (h4 - h5)
        w_pump_total = (1 - y - z) * w_pump1 + (1 - y) * w_pump2 + w_pump3
        w_net = w_turb - w_pump_total
        q_in = (h1 - h11) + (h3 - h2)
        eta = (w_net / q_in) * 100
        
        self.solution = (
            f"\n--- SOLUTION ---\n"
            f"State 1 (Turb In):       h1 = {h1:.2f} kJ/kg, s1 = {s1:.4f} kJ/kg-K\n"
            f"State 2 (Extraction):    h2 = {h2:.2f} kJ/kg\n"
            f"State 3 (After Reheat):  h3 = {h3:.2f} kJ/kg, s3 = {s3:.4f} kJ/kg-K\n"
            f"State 4 (Ext After):     h4 = {h4:.2f} kJ/kg\n"
            f"State 5 (Turb Out):      h5 = {h5:.2f} kJ/kg\n"
            f"State 6 (Pump 1 In):     h6 = {h6:.2f} kJ/kg\n"
            f"State 7 (Pump 1 Out):    h7 = {h7:.2f} kJ/kg\n"
            f"State 8 (Pump 2 In):     h8 = {h8:.2f} kJ/kg\n"
            f"State 9 (Pump 2 Out):    h9 = {h9:.2f} kJ/kg\n"
            f"State 10 (Pump 3 In):    h10 = {h10:.2f} kJ/kg\n"
            f"State 11 (Pump 3 Out):   h11 = {h11:.2f} kJ/kg\n\n"
            f"Extraction Fractions: y = {y:.4f}, z = {z:.4f}\n"
            f"Total Turbine Work: {w_turb:.2f} kJ/kg\n"
            f"Total Pump Work: {w_pump_total:.2f} kJ/kg\n"
            f"Total Heat Added: {q_in:.2f} kJ/kg\n"
            f"Thermal Efficiency: {eta:.2f}%"
        )


class CycleFactory:
    """Factory for creating Rankine cycle instances."""
    
    @staticmethod
    def create_cycle(cycle_type: str, **kwargs) -> RankineCycle:
        """Create a cycle instance based on type."""
        if cycle_type.lower() == "simple":
            return SimpleRankineCycle()
        elif cycle_type.lower() == "reheat":
            return ReheatRankineCycle(kwargs.get("num_reheats"))
        elif cycle_type.lower() == "regenerative":
            return RegenerativeRankineCycle(kwargs.get("num_fwh"))
        elif cycle_type.lower() == "regenerative_reheat":
            return RegenerativeReheatRankineCycle(kwargs.get("case_num"))
        else:
            raise ValueError(f"Unknown cycle type: {cycle_type}")


class CycleRunner:
    """Main application runner for interactive cycle selection and execution."""
    
    @staticmethod
    def run():
        """Run the interactive cycle problem generator."""
        cycles = [
            ("Simple Rankine Cycle", "simple", None),
            ("Reheat Rankine Cycle", "reheat", "num_reheats"),
            ("Regenerative Rankine Cycle", "regenerative", "num_fwh"),
            ("Regenerative-Reheat Rankine Cycle", "regenerative_reheat", "case_num")
        ]
        
        print("\nSelect a Rankine cycle type:")
        for i, (name, _, _) in enumerate(cycles, 1):
            print(f"{i}. {name}")
        
        while True:
            try:
                choice = int(input("Enter number (1-4): "))
                if 1 <= choice <= 4:
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        cycle_name, cycle_type, param_name = cycles[choice - 1]
        kwargs = {}
        
        if param_name:
            if param_name == "num_reheats":
                while True:
                    try:
                        num = int(input("Enter number of reheats (1-2): "))
                        if num in [1, 2]:
                            kwargs["num_reheats"] = num
                            break
                        else:
                            print("Invalid choice. Please enter 1 or 2.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            elif param_name == "num_fwh":
                while True:
                    try:
                        num = int(input("Enter number of Open FWHs (1-2): "))
                        if num in [1, 2]:
                            kwargs["num_fwh"] = num
                            break
                        else:
                            print("Invalid choice. Please enter 1 or 2.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            elif param_name == "case_num":
                while True:
                    try:
                        case = int(input("Enter case number (1-4): "))
                        if case in [1, 2, 3, 4]:
                            kwargs["case_num"] = case
                            break
                        else:
                            print("Invalid choice. Please enter 1, 2, 3, or 4.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
        
        cycle = CycleFactory.create_cycle(cycle_type, **kwargs)
        cycle.calculate()
        
        print(cycle.get_problem_statement())
        print(cycle.get_solution())


if __name__ == "__main__":
    CycleRunner.run()