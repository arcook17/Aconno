weight  = 246 #enter weight in lbs


HNT = .47*weight + 12
BUA = .08*weight - 2.9
BFO = .04*weight - 0.5
BH = .01*weight + 0.7
BUL = .18*weight + 3.2
BLL = .11*weight - 1.9
BF = .02*weight + 1.5

Total = HNT+BUA+BFO+BH+BUL+BLL+BF

#print(Total)

if Total != weight:
    diff = (weight - Total)/7
    HNT = HNT + diff
    BUA = BUA + diff
    BFO = BFO + diff
    BH = BH + diff
    BUL = BUL + diff
    BLL = BLL + diff
    BF = BF + diff

    Total_2 = HNT+BUA+BFO+BH+BUL+BLL+BF
    print("Entered Weight: ", weight, '\n')
    print("Head, Neck, Trunk: ", round(HNT,2),"lbs")
    print("Upper Arm: ", round(BUA,2),"lbs")
    print("Forearm: ",round(BFO,2),"lbs")
    print("Hand: ", round(BH,2),"lbs")
    print("Upper Leg: ", round(BUL,2),"lbs")
    print("Lower Leg: ", round(BLL,2),"lbs")
    print("Foot: ", round(BF,2),"lbs", '\n')
    print("TOTAL: ",round(Total_2,2),"lbs")
else:
    print("Entered Weight: ", weight, '\n')
    print("Head, Neck, Trunk: ", HNT)
    print("Upper Arm: ", BUA)
    print("Forearm: ", BFO)
    print("Hand: ", BH)
    print("Upper Leg: ", BUL)
    print("Lower Leg: ", BLL)
    print("Foot: ", BF,'\n')
    print("TOTAL: ", Total)



