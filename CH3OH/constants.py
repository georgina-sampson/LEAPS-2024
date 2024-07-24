SHOCK = 'c shock'
HOTCORE = 'hot core'
BOTH = 'both'

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

folder = '/data2/gsampsonolalde/LEAPS-2024/CH3OH/{}'
physical = {SHOCK: ['Density', 'gasTemp', 'av', 'zeta', 'radfield', SHOCKVEL],
            HOTCORE: ['Density', 'gasTemp', 'av', 'zeta', 'radfield'],
            BOTH: ['Density', 'gasTemp', 'av', 'zeta', 'radfield']}
species=['CH3OH']

initparams={
    SHOCK: [COSMICRAY, INTERSTELLARRAD, IDENS, SHOCKVEL],
    HOTCORE: [COSMICRAY, INTERSTELLARRAD, IDENS, FTEMP],
    BOTH: [COSMICRAY, INTERSTELLARRAD, IDENS, FTEMP, SHOCKVEL]
}

varPhys={
    SHOCK: ['gasTemp', 'av', 'Density'],
    HOTCORE: ['gasTemp'],
    BOTH: ['gasTemp', 'av', 'Density'],
}

SCATTER = 'scatter'
BAND = 'band'
JOINT = 'joint'
TIME = 'time'
ABUNDANCE = 'abundance'
CONTINUITY = 'continuity'

FINAL='Final'
TMAX='Max Temp'
SHOCKAVG= 'Inside Shock Average'
ALL= 'Full'

times={
    HOTCORE: [FINAL],
    SHOCK: [FINAL,TMAX,SHOCKAVG]
}