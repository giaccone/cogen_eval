import matplotlib.pyplot as plt

def bar_graph(Pt, Bt, Ut):
    """
    plot the energy demand over 24 h
    """
    hf1 = plt.figure()
    p1 = plt.bar(list(range(len(Pt))), Pt)
    p2 = plt.bar(list(range(len(Bt))), Bt, bottom=Pt)
    p3 = plt.plot(list(range(len(Ut))), Ut, 'k')
    plt.grid(True)
    plt.xlabel('hour', fontsize=14)
    plt.ylabel('thermal power (kW)', fontsize=14)
    plt.xlim(-1,24)
    plt.xticks(range(0, 24, 2), fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend((p1[0], p2[0], p3[0]),('Pt', 'Bt', 'Ut'), fontsize=12)
    plt.tight_layout()
    return hf1


def find_global_cost(etae, etat, Pmin, Pmax, Ptmin, Ptmax, etab, Bmax, Hi, cskW, cNGd, cNGnd, Deltat, Ut):
    """
    # cycle on the number of hours finding minimum cost option
    # --------------------------------------------------------
    #
    # evaluates minimum cost strategy comparing cogeneration and boiler costs
    # cycles over the number of intervals in the scheduling horizon given:
    #   - cost of natural gas (cHGd for CHP, cNGnd for Boiler)
    #   - physical property of Natural Gas (Hi lower heating value)
    #   - thermal load read from file Ut.csv
    #   - selling price of electricity read by file cs.csv
    #   - technical parameters of machines
    #      CHP etae, etat, Pmin, Pmax
    #      boiler etab, Bmax
    #
    # There are two options
    # option A all thermal load is produced by boiler
    # option B all thermal load is produced by CHP and if load is larger than CHP capacity the
    #   remainder is taken up by the boiler
    # the choice between the two options is the cost

    """
    Pe=[]
    Pt=[]
    Bt=[]
    GlobalCost=0
    ConvCost=0
    for thermal_load, cost in zip(Ut, cskW):
        # compute cost by boiler as reference
        BoilerCost = thermal_load / etab / Hi * cNGnd
        ConvCost = ConvCost + BoilerCost
        
        if thermal_load <= Ptmin:
            # load lower than minimum CHP value: only option is to run the boiler
            GlobalCost = GlobalCost + thermal_load * Deltat / etab / Hi * cNGnd
            
            Pe.append(0)
            Pt.append(0)
            Bt.append(thermal_load)
            
        else:
            Ut_residual = max(0, thermal_load - Ptmax) #defines the amount of heat that cannot be covered by CHP
            Ut_CHP = thermal_load - Ut_residual
            CHPcost = Ut_CHP * Deltat / etat / Hi * cNGd - Ut_CHP * Deltat / etat * etae * cost
            CHPcost = CHPcost + Ut_residual * Deltat / etab / Hi * cNGnd
            if CHPcost <= BoilerCost:
                Pe.append(Ut_CHP / etat * etae)
                Pt.append(Ut_CHP)
                Bt.append(Ut_residual)
                GlobalCost = GlobalCost + CHPcost
            else:
                Pe.append(0)
                Pt.append(0)
                Bt.append(thermal_load)
                GlobalCost = GlobalCost + BoilerCost
    
    return GlobalCost, Pe, Pt, Bt, ConvCost

