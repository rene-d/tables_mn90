' calculs MN90
'
' Ren_ DEVICHI - ao_t 2015
'
Option Explicit

Type modele
    nb_tissus   As Integer
    periode()    As Integer
    csc()          As Double
End Type

Dim vars_ok As Boolean              ' les paramtres ont _t_ initialis_ss

Dim gravitation As Double           ' gravitation en m/s
Dim dens As Double                  ' densit_ de l'eau en kg/l
Dim Patm As Double                  ' pression atmosph_rique
Dim pctN2 As Double                 ' pourcentage N2 dans l'air
Dim dp As Double                    ' distance entre paliers
Dim vr As Double                    ' vitesse entre fond et 1er palier
Dim vrp As Double                   ' vitesse entre paliers et palier-surface

Dim Pwvp As Double                  ' water vapor pressure
Dim use_schreiner As Boolean

Dim Cx As modele                    ' les compartiments
Dim GPS_lettre() As String
Dim GPS_n2() As Double

'
Function ceil(ByVal x As Double) As Double
    ceil = Excel.WorksheetFunction.Ceiling(x, 1)
End Function
'
Function en_minutes(ByVal temps As Double) As Double
    If temps > 0 And temps < 1 Then
        temps = temps * 24 * 60          ' conversion du temps en minutes
    End If
    en_minutes = temps
End Function
'
Sub init_vars(Optional ByVal force As Boolean = False)
    If vars_ok And Not force Then Exit Sub
    vars_ok = True
    
    ' valeurs par d_faut
    gravitation = 10#
    dens = 1#
    Patm = 1#
    pctN2 = 0.8
    dp = 3#
    vr = 15#
    vrp = 6#
        
    Pwvp = 0.0627
    use_schreiner = True
    
    Cx.nb_tissus = 12
    ReDim Cx.periode(1 To Cx.nb_tissus), Cx.csc(1 To Cx.nb_tissus)
     
    Cx.periode(1) = 5: Cx.csc(1) = 2.72
    Cx.periode(2) = 7: Cx.csc(2) = 2.54
    Cx.periode(3) = 10: Cx.csc(3) = 2.38
    Cx.periode(4) = 15: Cx.csc(4) = 2.2
    Cx.periode(5) = 20: Cx.csc(5) = 2.04
    Cx.periode(6) = 30: Cx.csc(6) = 1.82
    Cx.periode(7) = 40: Cx.csc(7) = 1.68
    Cx.periode(8) = 50: Cx.csc(8) = 1.61
    Cx.periode(9) = 60: Cx.csc(9) = 1.58
    Cx.periode(10) = 80: Cx.csc(10) = 1.56
    Cx.periode(11) = 100: Cx.csc(11) = 1.55
    Cx.periode(12) = 120: Cx.csc(12) = 1.54
    
    ReDim GPS_lettre(1 To 16), GPS_n2(1 To 16)
    GPS_lettre(1) = "A": GPS_n2(1) = 0.84
    GPS_lettre(2) = "B": GPS_n2(2) = 0.89
    GPS_lettre(3) = "C": GPS_n2(3) = 0.93
    GPS_lettre(4) = "D": GPS_n2(4) = 0.98
    GPS_lettre(5) = "E": GPS_n2(5) = 1.02
    GPS_lettre(6) = "F": GPS_n2(6) = 1.07
    GPS_lettre(7) = "G": GPS_n2(7) = 1.11
    GPS_lettre(8) = "H": GPS_n2(8) = 1.16
    GPS_lettre(9) = "I": GPS_n2(9) = 1.2
    GPS_lettre(10) = "J": GPS_n2(10) = 1.24
    GPS_lettre(11) = "K": GPS_n2(11) = 1.29
    GPS_lettre(12) = "L": GPS_n2(12) = 1.33
    GPS_lettre(13) = "M": GPS_n2(13) = 1.38
    GPS_lettre(14) = "N": GPS_n2(14) = 1.42
    GPS_lettre(15) = "O": GPS_n2(15) = 1.47
    GPS_lettre(16) = "P": GPS_n2(16) = 1.51
    
    get_param "dens", dens, 1, 1.05
    get_param "gravitation", gravitation, 9, 10
    get_param "vr", vr, 6, 20
    get_param "dp", dp, 1, 10
    get_param "Patm", Patm, 0.1, 1.1
    get_param "pctN2", pctN2, 0.2, 0.9
    
    get_param "Pwvp", Pwvp, 0#, 0.1
    get_param_bool "use_schreiner", use_schreiner
    
    Debug.Print "paramtres initialis_s"""
End Sub

Private Sub get_param_bool(ByVal nom As String, ByRef v As Boolean)
    Dim R As Range
    
    Set R = ActiveWorkbook.Names(nom).RefersToRange

    Dim x As Boolean
    On Error Resume Next
    x = R.Value
    If Err.Number <> 0 Then
        R.Value = v
    Else
        v = x
    End If
    On Error GoTo 0
    Debug.Print "PARAM "; nom; " = "; x
End Sub

Private Sub get_param(ByVal nom As String, ByRef v As Double, ByVal vmin As Double, ByVal vmax As Double)
    Dim R As Range
    
    Set R = ActiveWorkbook.Names(nom).RefersToRange
    If IsNumeric(R.Value) Then
        Dim x As String
        x = R.Value
        If vmin <= x And x <= vmax Then
            Debug.Print "PARAM "; nom; " = "; x
            v = x
        Else
            R.Value = "erreur"
        End If
    End If
End Sub
'
' initialisation des tissus _ la pression partielle de N2 en surface
'
Function init_tissus() As Double()
        Dim tissus() As Double
        Dim i As Integer
        ReDim tissus(1 To Cx.nb_tissus)
        For i = 1 To Cx.nb_tissus
            tissus(i) = Patm * pctN2
        Next
        init_tissus = tissus
End Function
'
' copie le tableau des tensions dans les tissus
'
Function deepcopy(tissus() As Double) As Double()
        Dim i As Integer
        Dim copie() As Double
        ReDim copie(1 To Cx.nb_tissus)
        For i = 1 To Cx.nb_tissus
            copie(i) = tissus(i)
        Next
        deepcopy = copie
End Function
'
' profondeur -> pression hydrostatique
'
Function calc_Phydro(ByVal prof As Double)
    calc_Phydro = prof / 100# * gravitation * dens
End Function
'
' profondeur -> Pabs
'
Function calc_Pabs(ByVal prof As Double)
    calc_Pabs = calc_Phydro(prof) + Patm
End Function
'
' Pabs -> profondeur
'
Function calc_prof(ByVal Pabs As Double)
    calc_prof = (Pabs - Patm) * 100# / gravitation / dens
End Function
'
' recherche la profondeur d'un palier en fonction de la Pabs _ ne pas d_passer
'
Function prof_palier(ByVal Ppalier As Double) As Double
    Dim palier As Double
    Dim i As Integer
    
    If Ppalier = 0 Then
        prof_palier = 0
        Exit Function
    End If
    
    palier = calc_prof(Ppalier)
    For i = 1 To 20
        If palier < dp * i + 1E-06 Then
            palier = dp * i
            Exit For
        End If
    Next
    
    prof_palier = palier
End Function
'
' calcul de la tension d'azote dans un tissu caract_ris_ par sa p_riode
'
Function calc_sat_tension(ByVal Ti As Double, ByVal Tf As Double, ByVal temps As Double, ByVal periode As Integer) As Double
    Dim g As Double           ' gradient
    Dim Tn2 As Double       ' tension aprs 'temps''
    
    g = 1 - 0.5 ^ (temps / periode)
    Tn2 = Ti + (Tf - Ti) * g
    
    calc_sat_tension = Tn2
End Function
'
' calcul de la dur_e de (d_)saturation
'
Function calc_sat_duree(ByVal Ti As Double, ByVal Tf As Double, ByVal Tn2 As Double, ByVal periode As Double) As Double
    Dim temps As Double     ' temps pour atteindre Tn2 en partant de Ti
    
    temps = Log(1 - (Tn2 - Ti) / (Tf - Ti)) / Log(0.5) * periode
    
    calc_sat_duree = temps
End Function
'
' recherche d'un palier
'
Sub calc_palier(ByVal prof As Double, ByVal temps As Double, ByRef tissus() As Double, ByRef Ppalier As Double, ByRef directeur As Integer)
    Dim Pf As Double        ' profondeur finale
    Dim Tf As Double        ' tension finale de N2
    Dim Ti As Double        ' tension initiale de N2
    Dim i As Integer
    Dim Tn2 As Double      ' tension de N2 au bout de 'temps'
    Dim Pcsc As Double         ' pression _ la sursaturation critique
    
    Pf = calc_Pabs(prof)
    Tf = pctN2 * Pf
    
    Ppalier = 0
    directeur = -1
 
    For i = 1 To Cx.nb_tissus
        Ti = tissus(i)
        
        Tn2 = calc_sat_tension(Ti, Tf, temps, Cx.periode(i))
    
        Pcsc = Tn2 / Cx.csc(i)
        If Pcsc > Patm And Ppalier < Pcsc Then
            Ppalier = Pcsc
            directeur = i
        End If
        
        tissus(i) = Tn2
    Next

End Sub
'
' calcul de la dur_e d'un palier, i.e. pour passer de 'prof' _ 'prof2'
'
Function calc_duree(ByVal prof As Double, ByVal prof2 As Double, ByVal Ti As Double, ByVal compartiment As Integer) As Double
    Dim Tf As Double
    Dim csc As Double
    Dim Ps As Double
    Dim Tn2 As Double
    
    Tf = pctN2 * calc_Pabs(prof)
    csc = Cx.csc(compartiment)
    Ps = calc_Pabs(prof2)
    Tn2 = csc * Ps  ' tension pour passer au palier suivant (ou _ la surface)

    calc_duree = Log(1 - (Tn2 - Ti) / (Tf - Ti)) / Log(0.5) * Cx.periode(compartiment)
End Function
'
' recherche du GPS correspondant _ une tension d'azote
'
Function calc_gps(ByVal n2 As Double) As String
    Dim i As Integer
    For i = 1 To UBound(GPS_lettre)
        If n2 < GPS_n2(i) Then
            calc_gps = GPS_lettre(i)
            Exit Function
        End If
    Next
    calc_gps = "*"
End Function
'
' calcul de la d_co et retourne un tableau avec 5 paliers max, la DTR et le GPS
'
Function calc_deco(ByVal prof As Double, ByVal temps As Double)
    Dim deco(6) As Variant
    Dim tissus() As Double
    Dim Ppalier As Double
    Dim directeur As Integer
    Dim premier_palier As Boolean
    Dim dtr As Double
    Dim palier As Double
    Dim tissus_palier() As Double
    Dim dr As Double
    Dim z As Double
    Dim d As Integer
    Dim duree_palier As Double
    Dim duree As Double
    Dim gps As String
    Dim nb_paliers As Integer
    Dim paliers(4)
    
    init_vars
    
    nb_paliers = 0
    
    tissus = init_tissus()
    Call calc_palier(prof, en_minutes(temps), tissus, Ppalier, directeur)
           
    premier_palier = True
    dtr = 0

    Do While True
        palier = prof_palier(Ppalier)

        If premier_palier And palier <> 0 Then
            ' est-ce que la remont_e permet de d_saturer suffisamment ?

            tissus_palier = deepcopy(tissus)
            dr = (prof - palier) / IIf(premier_palier, vr, vrp)
            
            Call calc_palier((prof + palier) / 2#, dr, tissus_palier, z, d)

            If prof_palier(z) = palier - dp Then
                palier = palier - dp
            End If
        End If

        dr = (prof - palier) / IIf(premier_palier, vr, vrp)
        premier_palier = False
        dtr = dtr + dr

        ' d_sat moyenne pendant la remont_e jusqu'au premier palier
        Call calc_palier((prof + palier) / 2#, dr, tissus, z, d)
        
        If Ppalier = 0 Or d = -1 Then
            Exit Do
        End If
        
        duree_palier = 0#
        tissus_palier = deepcopy(tissus)
        Do While True
            duree = calc_duree(palier, palier - dp, tissus_palier(d), d)
            duree_palier = duree_palier + duree
            Call calc_palier(palier, duree, tissus_palier, Ppalier, d)
            If d = -1 Then Exit Do                                  ' fin de la plong_e
            If prof_palier(Ppalier) < palier Then Exit Do   ' changement de palier
        Loop
        
        duree_palier = ceil(duree_palier)
        dtr = dtr + duree_palier
        
        'Debug.Print "PALIER _ ", palier; "m", ":", duree_palier; "'"
        
        ' dans Excel on limite _ 5 paliers, sinon trop de valeurs retourn_es
        If nb_paliers = 5 Then
            deco(0) = "trop de paliers"
            calc_deco = deco
            Exit Function
        End If
        
        paliers(nb_paliers) = duree_palier
        nb_paliers = nb_paliers + 1
        
        Call calc_palier(palier, duree_palier, tissus, Ppalier, directeur)
        prof = palier
    Loop
    
    dtr = ceil(dtr)
    gps = calc_gps(tissus(Cx.nb_tissus))

    'Debug.Print "DTR", dtr
    'Debug.Print "GPS", gps
    
    Dim i As Integer
    For i = 0 To 4
        If nb_paliers >= 5 - i Then
            deco(i) = paliers(nb_paliers - 5 + i)
        Else
            deco(i) = ""
        End If
    Next
    
    deco(5) = dtr
    deco(6) = gps
    
    calc_deco = deco
    
End Function
'
' calcul de d_co en retournant un tableau vertical
'
Function calc_decov(ByVal prof As Double, ByVal temps As Double)
    Dim decov(6, 0) As Variant
    Dim deco() As Variant
    Dim i As Integer
    deco = calc_deco(prof, temps)
    For i = 0 To 6
        decov(i, 0) = deco(i)
    Next
    calc_decov = decov
End Function
'
' calcul de l'azote r_siduel en fonction de la dur_e et du GPS
'
Function residuel(gps As String, temps As Double) As Double
    Dim i As Integer
    init_vars
    For i = 1 To UBound(GPS_lettre)
        If GPS_lettre(i) = gps Then
            residuel = calc_sat_tension(GPS_n2(i), pctN2 * Patm, en_minutes(temps), 120)
            Exit Function
        End If
    Next
End Function
'
' calcul de l'azote r_siduel en fonction de la dur_e et du GPS
'
Function o2pur(n2_debut As Double, temps As Double) As Double
    init_vars
    o2pur = calc_sat_tension(n2_debut, 0, en_minutes(temps), 240)
End Function
'
' calcul de la majoration _ partir d'une tension d'azote r_siduel
'
Function majoration(ByVal n2 As Double, ByVal prof As Integer) As Integer
    init_vars
    majoration = calc_sat_duree(Patm * pctN2, pctN2 * calc_Pabs(prof), n2, 120)
End Function
'
'
'
Function calc_schreiner(Pabs As Double, Ti As Double, temps As Double, periode As Double, R As Double)
    Dim Palv As Double
    Dim k As Double
    Dim P As Double
    Dim P2 As Double
    
    init_vars
    
    If use_schreiner Then
        Palv = pctN2 * (Pabs - Pwvp)
        k = Log(2) / periode
        P = Palv + R * (temps - 1 / k) - (Palv - Ti - R / k) * Exp(-k * temps)
        calc_schreiner = P
    
    Else
        Dim Tf As Double
        
        Tf = pctN2 * Pabs
        If R <> 0 Then
            Tf = (Ti + Tf + R * temps) / 2
        End If
        
        P = calc_sat_tension(Ti, Tf, temps, periode)
     
    End If
        
    calc_schreiner = P
End Function

Sub recalculer()
    Dim w As Excel.Worksheet
    
    For Each w In Worksheets
        w.UsedRange.Dirty
        w.Calculate
    Next
    Exit Sub
    
    Dim c As Excel.Range
    Dim ar As New Collection
    w.Unprotect
    For Each c In w.UsedRange
        If c.HasFormula Then
            If Not c.HasArray Then
                Debug.Print "recalculate", c.Address, c.Formula
                c.Dirty
                c.Calculate
            Else
                On Error Resume Next
                ar.Add c.CurrentArray, c.CurrentArray.Address
                On Error GoTo 0
            End If
        End If
    Next
    For Each c In ar
        'Debug.Print "array:", c.Address, c.FormulaArray
        c.Dirty
        c.Calculate
    Next
    w.Protect DrawingObjects:=True, Contents:=True, Scenarios:=True
End Sub
'
'
'
Sub charger_profil()
    Dim w As Worksheet
    Dim num As Integer
    Dim R As Range
    
    Set w = Worksheets("Exemples de profil")
    num = w.Range("A1").Value
    
    Set R = w.Cells(12 + num * 5, 2)
    Set R = w.Range(R, R.Offset(3, 9))
    
    R.Copy Worksheets("Tensions").Range("E3:N6")
End Sub
'
'
'
Sub recalculer_tensions()
    Dim w As Worksheet
    
    init_vars True
    
    Set w = Worksheets("Tensions")
    w.UsedRange.Dirty
    w.Calculate
End Sub
