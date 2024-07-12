SHOCK = 'c shock'
HOTCORE = 'hot core'

ITEMP = 'iTemp'
FTEMP = 'fTemp'
IDENS = 'iDens'
FDENS = 'fDens'
SHOCKVEL = 'shockVel'
COSMICRAY = 'cosmicRay'
INTERSTELLARRAD = 'interstellarRad'
FTIME = 'fTime'
ROUT = 'rout'
BAV = 'bAv'

PHASE1 = 'startData'
PHASE2 = 'modelData'

initparams={
    SHOCK: [COSMICRAY, INTERSTELLARRAD, IDENS, SHOCKVEL],
    HOTCORE: [COSMICRAY, INTERSTELLARRAD, IDENS, FTEMP],
}

varPhys={
    SHOCK: ['gasTemp', 'av', 'Density'],
    HOTCORE: ['gasTemp']
}

SCATTER = 'scatter'
BAND = 'band'
JOINT = 'joint'
TIME = 'time'
ABUNDANCE = 'abundance'

FINAL='Final'
TMAX='Max Temp'
SHOCKAVG= 'Inside Shock Average'