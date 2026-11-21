import pandas as pd, json, re, sys
from collections import defaultdict
SRC='nba-trades-database/data/clean/'  # path to a clone of brucegav/nba-trades-database
OUT='data/trades.json'
d=pd.read_csv(SRC+'player_trades_clean.csv')
p=pd.read_csv(SRC+'draft_pick_trades_clean.csv')
def pdate(s):
    m,dd,y=[int(x) for x in s.split('-')]
    y = 1900+y if y>=46 else 2000+y
    return y*10000+m*100+dd
d['dn']=d.date.map(pdate); p['dn']=p.date.map(pdate)
d['sy']=d.season.str[:4].astype(int)
d=d[(d.sy>=1996)&(d.sy<=2025)].copy()
# known data fixes
d.loc[(d.trade_id=='19-22')&(d.player=='anthony davis'),'sending_team']='pelicans'
for pl in ['jalen green','dillon brooks','khaman maluach']:
    d.loc[(d.trade_id=='25-13')&(d.player==pl),'receiving_team']='suns'
FR={'hawks':'ATL','celtics':'BOS','nets':'BKN','bobcats':'CHA','bulls':'CHI','cavaliers':'CLE','mavericks':'DAL','nuggets':'DEN','pistons':'DET','warriors':'GSW','rockets':'HOU','pacers':'IND','clippers':'LAC','lakers':'LAL','grizzlies':'MEM','heat':'MIA','bucks':'MIL','timberwolves':'MIN','pelicans':'NOP','knicks':'NYK','thunder':'OKC','supersonics':'OKC','magic':'ORL','sixers':'PHI','suns':'PHX','trail blazers':'POR','kings':'SAC','spurs':'SAS','raptors':'TOR','jazz':'UTA','wizards':'WAS'}
def fr(t,dt):
    if t=='hornets':
        return 'CHA' if dt<20020701 or dt>=20140520 else 'NOP'
    return FR[t]
TEAMS=['BOS','BKN','NYK','PHI','TOR','CHI','CLE','DET','IND','MIL','ATL','CHA','MIA','ORL','WAS',
       'DEN','MIN','OKC','POR','UTA','GSW','LAC','LAL','PHX','SAC','DAL','HOU','MEM','NOP','SAS']
TI={t:i for i,t in enumerate(TEAMS)}
SPECIAL={'lebron':'LeBron','demar':'DeMar','derozan':'DeRozan','deandre':'DeAndre','demarcus':'DeMarcus','javale':'JaVale','lamarcus':'LaMarcus','lamelo':'LaMelo','dangelo':"D'Angelo",'deaaron':"De'Aaron",'oneal':"O'Neal",'oneale':"O'Neale",'jamychal':'JaMychal','demarre':'DeMarre','dejounte':'Dejounte','dasean':'DaSean','javonte':'JaVonte','tyreke':'Tyreke','deshawn':'DeShawn','dequan':'DeQuan','daequan':'Daequan','jaquez':'Jaquez','lavine':'LaVine','mcgrady':'McGrady','okafor':'Okafor','iii':'III','ii':'II','iv':'IV','jr':'Jr.','sr':'Sr.','deron':'Deron','demetrius':'Demetrius','delonte':'Delonte','dewayne':'DeWayne','jajuan':'JaJuan','kentavious':'Kentavious','dedmon':'Dedmon','deanthony':'DeAnthony','andre':'Andre','juwan':'Juwan','lamar':'Lamar','kevin':'Kevin','shai':'Shai','dejuan':'DeJuan','tremont':'Tremont','denzel':'Denzel','damarcus':'Damarcus','gilgeous':'Gilgeous'}
INIT={'pj','cj','tj','rj','dj','jj','aj','og','kj','jr','jt','tj','jb','bj','jp','dt','jk','rj','cj','gg','pj','jd','ej','kc','mj','dj'}
def nice(n):
    hy={'shai gilgeous alexander':'Shai Gilgeous-Alexander','shareef abdur rahim':'Shareef Abdur-Rahim','al farouq aminu':'Al-Farouq Aminu','michael kidd gilchrist':'Michael Kidd-Gilchrist','karl anthony towns':'Karl-Anthony Towns','nigel hayes davis':'Nigel Hayes-Davis','jalen hood schifino':'Jalen Hood-Schifino','talen horton tucker':'Talen Horton-Tucker','dorian finney smith':'Dorian Finney-Smith','luka doncic':'Luka Dončić','nikola jokic':'Nikola Jokić','dario saric':'Dario Šarić','bojan bogdanovic':'Bojan Bogdanović','jusuf nurkic':'Jusuf Nurkić','kristaps porzingis':'Kristaps Porziņģis','yanic konan niederhauser':'Yanic Konan Niederhäuser','kasparas jakucionis':'Kasparas Jakučionis','vlade divac':'Vlade Divac','peja stojakovic':'Peja Stojaković','hedo turkoglu':'Hedo Türkoğlu','marcin gortat':'Marcin Gortat','dennis schroder':'Dennis Schröder','timothe luwawu cabarrot':'Timothé Luwawu-Cabarrot','rondae hollis jefferson':'Rondae Hollis-Jefferson','willie cauley stein':'Willie Cauley-Stein','kentavious caldwell pope':'Kentavious Caldwell-Pope','nickeil alexander walker':'Nickeil Alexander-Walker','jaren jackson jr':'Jaren Jackson Jr.','metta world peace':'Metta World Peace','ron artest':'Ron Artest','kelly oubre jr':'Kelly Oubre Jr.'}
    if n in hy: return hy[n]
    out=[]
    for w in n.split():
        if w in SPECIAL: out.append(SPECIAL[w])
        elif w in INIT: out.append(w.upper())
        elif w.startswith('mc') and len(w)>3: out.append('Mc'+w[2:].capitalize())
        else: out.append(w.capitalize())
    return ' '.join(out)
def nice_notes(s):
    s=re.sub(r'\(([^)]*)\)', lambda m: '('+ (m.group(1) if m.group(1) in ('did not convey',) else nice(m.group(1).strip())) +')', s)
    s=re.sub(r'(\d{4}) (1st|2nd) rounder', lambda m: f'{m.group(1)} {m.group(2)}-round pick', s)
    for k,v in [('trail blazers','Trail Blazers'),('sixers','76ers'),('supersonics','SuperSonics'),('timberwolves','Timberwolves')]:
        s=re.sub(r'\b'+k+r'\b',v,s)
    s=re.sub(r'\b(hawks|celtics|nets|bobcats|hornets|bulls|cavaliers|mavericks|nuggets|pistons|warriors|rockets|pacers|clippers|lakers|grizzlies|heat|bucks|pelicans|knicks|thunder|magic|suns|kings|spurs|raptors|jazz|wizards)\b', lambda m:m.group(1).capitalize(), s)
    s=s.replace('->',' → ').replace(', ',' · ')
    return s
players=[]; PI={}
def pid(n):
    if n not in PI: PI[n]=len(players); players.append(nice(n))
    return PI[n]
trades=[]
pk=defaultdict(list)
for _,r in p.iterrows():
    pk[r.trade_id].append(r)
for tid,g in d.groupby('trade_id', sort=False):
    dt=int(g.dn.min()); sy=int(g.sy.iloc[0])
    legs=[]
    for _,r in g.iterrows():
        a=TI[fr(r.sending_team,r.dn)]; b=TI[fr(r.receiving_team,r.dn)]
        legs.append([pid(r.player),a,b])
    notes=[nice_notes(x) for x in dict.fromkeys(n for n in g.draft_pick_notes if isinstance(n,str))]
    picks=[]
    for r in pk.get(tid,[]):
        try:
            a=TI[fr(r.sending_team,r.dn)]; b=TI[fr(r.receiving_team,r.dn)]
        except KeyError: continue
        if a!=b: picks.append([a,b])
    t={'id':tid,'d':dt,'s':sy,'l':legs}
    if notes: t['n']=notes
    if picks: t['p']=[list(x) for x in {tuple(x) for x in picks}]
    trades.append(t)
trades.sort(key=lambda t:(t['d'],t['id']))
selfl=sum(1 for t in trades for l in t['l'] if l[1]==l[2])
print('trades',len(trades),'legs',sum(len(t['l']) for t in trades),'players',len(players),'self',selfl, file=sys.stderr)
out={'source':'brucegav/nba-trades-database (scraped from Basketball-Reference), commit f852052','teams':TEAMS,'players':players,'trades':trades}
s=json.dumps(out,separators=(',',':'),ensure_ascii=False)
open(OUT,'w').write(s); print(len(s), file=sys.stderr)
