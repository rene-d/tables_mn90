#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set ts=4 sw=4 et:

# René DEVICHI 2015/08/05

# dédicacé à Christian Aragon

# rappels
#  hectopascal (hPa) : 1 hPa = 100 Pa = 100 N⋅m⁻² = 1 mbar (millibar)
#  newton (N) : 1 N = 1 kg⋅m⋅s⁻²

from __future__ import print_function
import sys
import math
import copy
import argparse
 

verbose = False

gravitation = 10.0          # accélération terrestre en m/s²
dens = 1.0                  # densité de l'eau en kg/l
Patm = 1.0                  # pression atmosphérique en bar
 
pctN2 = 0.8                 # pourcentage de N₂ dans l'air
 
dp = 3.0                    # espacement des paliers en mètre
vr = 15.0                   # vitesse de remontée en m/min fond -> 1er palier
vrp = 6.0                   # vitesse de remontée en m/min entre paliers

Pwvp = 0.0627               # water vapor pression (pression de la vapeur d'eau à 37°C)
 
##
# @brief compartiments (période, csc)
#
C = [ (  5, 2.72),
      (  7, 2.54),
      ( 10, 2.38),
      ( 15, 2.20),
      ( 20, 2.04),
      ( 30, 1.82),
      ( 40, 1.68),
      ( 50, 1.61),
      ( 60, 1.58),
      ( 80, 1.56),
      (100, 1.55),
      (120, 1.54),
    ]
   
##
# @brief limite des groupes de plongées successives
#
GPS = [ ( 'A', 0.84 ),
        ( 'B', 0.89 ),
        ( 'C', 0.93 ),
        ( 'D', 0.98 ),
        ( 'E', 1.02 ),
        ( 'F', 1.07 ),
        ( 'G', 1.11 ),
        ( 'H', 1.16 ),
        ( 'I', 1.20 ),
        ( 'J', 1.24 ),
        ( 'K', 1.29 ),
        ( 'L', 1.33 ),
        ( 'M', 1.38 ),
        ( 'N', 1.42 ),
        ( 'O', 1.47 ),
        ( 'P', 1.51 ),
      ]

##
# @brief table MN90 profondeur/temps
#
MN90 = [ (  6, '15 30 45 75 105 135 180 240 315 360' ),
         (  8, '15 30 45 60 90 105 135 165 205 255 300 360' ),
         ( 10, '15 30 45 60 75 105 120 135 165 180 240 255 315 330 360' ),
         ( 12, '5 15 25 35 45 55 65 80 90 105 120 135 140 150 160 170 180 190 200 210 220 230 240 250 255 270 285 300 315 330 360' ),
         ( 15, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 115 120 130 140' ),
         ( 18, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 115 120 130 140 150' ),
         ( 20, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 115 120' ),
         ( 22, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 115 120' ),
         ( 25, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 115 120' ),
         ( 28, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 115 120' ),
         ( 30, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90' ),
         ( 32, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90' ),
         ( 35, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90' ),
         ( 38, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90' ),
         ( 40, '5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90' ),
         ( 42, '5 10 15 20 25 30 35 40 45 50 55 60' ),
         ( 45, '5 10 15 20 25 30 35 40 45 50 55 60' ),
         ( 48, '5 10 15 20 25 30 35 40 45 50 55 60' ),
         ( 50, '5 10 15 20 25 30 35 40 45 50 55 60' ),
         ( 52, '5 10 15 20 25 30 35 40 45 50 55 60' ),
         ( 55, '5 10 15 20 25 30 35 40 45 50 55 60' ),
         ( 58, '5 10 15 20 25 30 35 40 45 50 55 60' ),
         ( 60, '5 10 15 20 25 30 35 40 45 50 55 60' ),
         ( 62, '5 10 15' ),
         ( 65, '5 10 15' ),
       ]
       
 
def print_verbose(*args):
    if verbose:
        print(*args)


def init_tissus():
    tissus = dict()
    for periode, csc in C:
        # compartiment spécial
        if periode == 240: continue
        tissus[periode] = pctN2 * Patm
    return tissus
 

##
# @brief meter of salt water
#        nombre de bar / mètre d'eau (typiquement: 0.1)
#
# @return 
def msw():
    return gravitation * dens / 100.

##
# @brief calcule la pression hydrostatique
#
# @param prof hauteur de la colonne d'eau en mètre
#
# @return pression en bar
#
def calc_Phydro(prof):
    return prof * msw()

##
# @brief calcule la pression absolue en fonction d'une profondeur
#
# @param prof hauteur de la colonne d'eau
#
# @return pression absolue correspondante
def calc_Pabs(prof):
    return Patm + calc_Phydro(prof)


##
# @brief calcule une profondeur en fonction de la pression absolue
#
# @param Pabs pression absolue
#
# @return hauteur de la colonne d'eau correspondante
#
def calc_prof(Pabs):
    return (Pabs - Patm) / msw()
    

##
# @brief cherche la profondeur d'un palier pour ne pas dépasser la pression hydrostatique
#
# @param Ppalier pression hydrostatique max
#
# @return profondeur du palier en mètre
#
def prof_palier(Ppalier):
    if Ppalier is None:
        return 0
    palier = calc_prof(Ppalier)
    for i in range(1, 11):
        if palier < dp * i + 0.000001:
            palier = dp * i
            break
    return palier



##
# @brief calcul de la saturation d'un tissu
#
# @param Ti tension initiale
# @param Tf tension finale
# @param temps durée de saturation
# @param periode période du tissu (temps de demi saturation)
#
# @return la tension au bout de 'temps'
def calc_sat_tension(Ti, Tf, temps, periode):

    g = 1 - math.pow(0.5, temps / float(periode))
    Tn2 = Ti + (Tf - Ti) * g

    return Tn2


def calc_sat_duree(Ti, Tf, Tn2, periode):
    
    temps = math.log(1 - (Tn2 - Ti) / (Tf - Ti)) / math.log(0.5) * periode
    
    return temps


##
# @brief 
#
# @param Pabs
# @param Ti
# @param temps
# @param periode
# @param R
#
# @return 
def calc_schreiner(Pabs, Ti, temps, periode, R):
    Palv = pctN2 * (Pabs - Pwvp)
    k = math.log(2) / periode
    P = Palv + R * (temps - 1 / k) - (Palv - Ti - R / k) * math.exp(-k * temps)
    return P


##
# @brief calcule la saturation dans les tissus selon les compartiments MN90
#
# @param prof
# @param temps
# @param tissus
# @param titre
#
# @return la pression à ne pas dépasser et le compartiment directeur
def calc_palier(prof, temps, tissus, titre="calc_palier"):
    print_verbose()
    print_verbose(">>>>>>", titre)
    print_verbose("prof=", prof, "temps=", temps)
    Pf = calc_Pabs(prof)
    Tf = pctN2 * Pf
    print_verbose("Pf={} Tf={}".format(Pf, Tf))
 
    Ppalier = None
    directeur = None
 
    for periode, csc in C:       
        # cas spécial pour calcul avec C120 ou C240 uniquement
        if not periode in tissus: continue

        Ti = tissus[periode]
      
        Tn2 = calc_sat_tension(Ti, Tf, temps, periode)
       
        c = Tn2 / csc
        if c > Patm and Ppalier < c:
            Ppalier = c
            directeur = (periode, csc)

        tissus[periode] = Tn2

        if c > Patm:
            stop = "stop {:6.4f} m".format(calc_prof(c))
        else:  
            stop = ""
 
        print_verbose("{:3.0f} Ti={:7.5f} Tf={:7.5f} Tn2={:7.5f} {:7.5f} {}".format(periode, Ti, Tf, Tn2, c, stop))
       
    if not directeur is None:
        print_verbose("il faut faire un palier à au moins {:3.3f} m".format(calc_prof(Ppalier)))
        pass

    return Ppalier, directeur


##
# @brief cherche la durée qu'il faut pour qu'un tissu passe à une certaine tension de N2
#
# @param prof
# @param prof2
# @param Ti
# @param compartiment
#
# @return 
def calc_duree(prof, prof2, Ti, compartiment):
    print_verbose()
    print_verbose("calc_duree", prof, prof2, Ti, compartiment)
    Pf = calc_Pabs(prof)
    Tf = pctN2 * Pf

    csc = compartiment[1]

    Ps = calc_Pabs(prof2)

    Tn2 = csc * Ps  # tension pour passer au palier suivant (ou à la surface)

    print_verbose("Tn2=", Tn2, "Ti=",Ti, "Tf=", Tf)

    duree = calc_sat_duree(Ti, Tf, Tn2, float(compartiment[0]))
    print_verbose("duree=", duree * 60, "s")
    return duree

    

def calc_gps(Tn2):
    Tn2 = round(Tn2, 2)
    for gps, limite in GPS:
        if Tn2 > limite: continue
        if Tn2 <= limite: return gps
    return "*"


##
# @brief calcule les paliers selon l'algo MN90
#
# @param prof
# @param temps
#
# @return 
def calc_deco(prof, temps):    
    deco = dict()
    
    print_verbose("DECO prof={} m temps={} min".format(prof, temps))
    deco['prof'] = prof
    deco['temps'] = temps
    deco['paliers'] = []

    tissus = init_tissus()    
    Ppalier, _ = calc_palier(prof, temps, tissus, titre="tissus après la plongée")
           
    premier_palier = True
    dtr = 0

    while True:
       
        palier = prof_palier(Ppalier) 

        if premier_palier and palier != 0:
            # est-ce que la remontée permet de désaturer suffisamment ?

            tissus_palier = copy.deepcopy(tissus)
            dr = (prof - palier) / (vr if premier_palier else vrp)
            
            z, d = calc_palier((prof + palier) / 2., dr, tissus_palier, titre="test désat pendant remontée à {} m".format(palier))

            if prof_palier(z) == palier - dp:
                print_verbose("le palier à {} m n'est pas nécessaire".format(palier))
                palier = palier - dp


        dr = (prof - palier) / (vr if premier_palier else vrp)
        premier_palier = False
        dtr += dr

        print_verbose("durée remontée de {} m à {} m : {} s".format(prof, palier, dr * 60))

        # désat moyenne pendant la remontée jusqu'au premier palier
        z, d = calc_palier((prof + palier) / 2., dr, tissus, titre="tissus après la remontée au palier de {} m".format(palier))
        print_verbose("directeur après remontée -->", z, d)

        if Ppalier is None or d is None:
            break
       
        # il faut trouver la durée telle que
        #   Tn2 = Ti + (Tf - Ti) * (1 - 0.5^(duree/d))
        #   avec Ti = tissus[d]
        #        Tf = tension au palier suivant
        #        Tn2 / csc = pression absolue au palier suivant

        duree_palier = 0
        tissus_palier = copy.deepcopy(tissus)
        while True:
            duree = calc_duree(palier, palier - dp, tissus_palier[d[0]], d)
            print_verbose("DUREE -----> {:.3f} s".format(duree * 60))
            duree_palier += duree
            Ppalier, d = calc_palier(palier, duree, tissus_palier, titre="tissus au bout de {:4.1f} s au palier de {} m".format(duree_palier * 60, palier))
            if d is None: break                     # fin de la plongée
            if prof_palier(Ppalier) < palier: break # changement de palier

        duree_palier = int(math.ceil(duree_palier))
        dtr += duree_palier
        print_verbose("DUREE TOTALE PALIER A {} m ---> {} min".format(palier, duree_palier))
        
        deco['paliers'].append((palier, duree_palier))

        Ppalier, _ = calc_palier(palier, duree_palier, tissus, titre="tissus après le palier à {} m".format(palier))
        prof = palier
        
    dtr = int(math.ceil(dtr))
    gps = calc_gps(tissus[120])
    
    print_verbose("DTR: {} min".format(dtr))
    print_verbose("GPS: {}".format(gps))
       
    deco['DTR'] = dtr
    deco['GPS'] = gps

    return deco

    
##
# @brief affiche les paliers simplement
#
# @param deco
#
# @return 
def print_deco(deco):
    print("Prof: {} m, temps: {} min".format(deco['prof'], deco['temps']))
    for p, d in deco['paliers']:
        print("Palier à {:5} m : {} min".format(p, d))
    print("DTR: {} min".format(deco['DTR']))
    print("GPS: {}".format(deco['GPS']))
    
    
##
# @brief calcule toute la table MN90
#
# @param tprof
# @param ttemps
#
# @return 
def calc_table(tprof=None, ttemps=None):

    mp = 0
    table = []
    pprof = []
    for prof, durees in MN90:    
        if not tprof is None and tprof != prof: continue
        for temps in durees.split():       
            temps = int(temps)
            if not ttemps is None and ttemps != temps: continue
            deco = calc_deco(prof, temps)
            if mp < len(deco['paliers']):
                mp = len(deco['paliers']) 
                pprof = []
                for p, _ in deco['paliers']:
                    pprof.append(p)
            table.append(deco)

    if True:                
        sep = "+".ljust(7, "-")
        for i in range(0, mp): 
            sep += "+".ljust(8, "-")
        sep += "+------+-----+"

        prof = None
        for deco in table:                
            if prof != deco['prof']:
                prof = deco['prof']            
                s = "| {:3}m ".format(prof)
                for p in pprof:
                    s += "| {:4.1f}m ".format(p)
                s += "|  DTR | GPS |"

                print(sep)
                print(s)
                print(sep)

            s = "| {:3}' ".format(deco['temps'])           
            for i in range(0, mp - len(deco['paliers'])):
                s += "|       "             
            for p, d in deco['paliers']:
                s += "|  {:3}' ".format(d)            
            s += "| {:3}' |  {}  |".format(deco['DTR'], deco['GPS'])            
            print(s)
            
        print(sep)
        
    else:
        sep = "+--------------------"
        for i in range(0, mp): 
            sep += "+".ljust(11, "-")
        sep += "+-----------+--------+"
        
        prof = None
        for deco in table:    
            if prof != deco['prof']:
                print(sep)
                prof = deco['prof']
            
            s = "| Prof: {:2}m, t: {:3}' ".format(deco['prof'], deco['temps'])           
            for i in range(0, mp - len(deco['paliers'])):
                s += "|".ljust(11)     
            for p, d in deco['paliers']:
                s += "| {:2g}m {:3}' ".format(p, d)
            s += "| DTR: {:3}' | GPS: {} |".format(deco['DTR'], deco['GPS'])            
            print(s)
            
        print(sep)

    
##
# @brief affiche un message d'erreur puis l'aide
#
# @param parser
# @param errmsg
#
# @return 
def erreur(parser, errmsg):
    print("Erreur:", errmsg)
    print()
    parser.print_help()
    sys.exit(2)
    pass


def ensure(a, b, x):
    try:
        x = float(x)
        if not (a <= x and x <= b):
            msg = "%r doit être un float entre %r et %r" % (x, a, b)
            raise argparse.ArgumentTypeError(msg)
    except ValueError:
        msg = "%r n'est pas un float" % x
        raise argparse.ArgumentTypeError(msg)
    return x

def frange(a, b):
    return lambda x: ensure(a, b, x)


def main():
    global verbose
    global dens, dp, vr, vrp, pctN2, Patm, gravitation
    global Pwvp

    prof = None
    temps = None
    
    parser = argparse.ArgumentParser(description="Calculs paliers MN90")
    parser.add_argument("-v", help="mode verbeux", action="store_true", dest="verbose")
    parser.add_argument("-p", type=int, help="profondeur en mètres", dest="prof")
    parser.add_argument("-t", type=int, help="temps en minutes", dest="temps")
    parser.add_argument("-dp", type=frange(1, 9), help="distance entre paliers en mètres", dest="dp")
    parser.add_argument("-d", type=frange(0.8, 1.4), help="densité de l'eau en kg/l", dest="dens")
    parser.add_argument("-grav", type=frange(9, 11), help="gravitation terrestre", dest="gravitation", metavar="ACCEL")
    parser.add_argument("-patm", type=frange(0.6, 1.1), help="pression atmosphérique en bar", dest="Patm", metavar="BAR")
    parser.add_argument("-vr", type=frange(6, 20), help="vitesse de remontée en m/min", dest="vr")
    parser.add_argument("-n2", type=frange(0.1, 0.9), help="fraction de N2 dans l'air respiré", dest="pctN2", metavar="%N2")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-table", help="calcul de la table MN90 entière", action="store_true", dest="mn90")
    group.add_argument("-residuel", type=str, help="détermination de l'azote résiduel", metavar="GPS")
    group.add_argument("-majoration", type=frange(0.78, 1.54), help="détermination de la majoration", metavar="N2")
    group.add_argument("-o2pur", type=frange(0.78, 1.54), help="diminution de l'azote résiduel avec O2 pur", metavar="N2")

    parser.add_argument("-wvp", type=frange(0, 0.1), help="pression vapeur d'eau (0.0627 par défaut) dans la formule de Schreiner", dest="Pwvp", metavar="BAR")

    args = parser.parse_args()
    
    # globalisation des arguments de ligne de commande
    verbose = args.verbose
    if not args.dp is None: dp = args.dp
    if not args.dens is None: dens = args.dens
    if not args.gravitation is None: gravitation = args.gravitation
    if not args.Patm is None: Patm = args.Patm
    if not args.vr is None: vr = args.vr
    if not args.pctN2 is None: pctN2 = args.pctN2
    if not args.Pwvp is None: Pwvp = args.Pwvp
    
    if args.mn90:
        calc_table(args.prof, args.temps)

    elif not args.residuel is None:
        if args.temps is None:
            erreur(parser, "-t est nécessaire")

        for gps, n2 in GPS:
            if gps == args.residuel:
                r = calc_sat_tension(n2, pctN2 * Patm, args.temps, 120)
                print("Azote résiduel pour GPS={} après {} min: {:.2f}".format(gps, args.temps, r))

    elif not args.majoration is None:
        if args.prof is None:
            erreur(parser, "-p est nécessaire")

        # le csc passé en paramètre est un artifice pour que Tn2 soit égal à args.majoration
        # dans la fonction
        majo = int(math.ceil(calc_duree(args.prof, 0, pctN2 * Patm, (120, args.majoration / Patm))))
        print("Majoration pour un azote résiduel {:.2f} et une profondeur de {} m : {} min".format(args.majoration, args.prof, majo))

    elif not args.o2pur is None:
        if args.temps is None:
            erreur(parser, "-t est nécessaire")

        # C240: effet vasoconstricteur de l'oxygène
        r = calc_sat_tension(args.o2pur, 0, args.temps, 240)
        print("Diminution azote résiduel pour {:.2f} après {} min: {:.2f}".format(args.o2pur, args.temps, r))

    else:
        if args.prof is None or args.temps is None:
            erreur(parser, "-p et -t sont nécessaires")

        deco = calc_deco(args.prof, args.temps)
        print_deco(deco)


if __name__ == "__main__":
    main()
    pass
