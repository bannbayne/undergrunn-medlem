import os

src_file = r'c:\Users\josou\Downloads\NORSK AUTOTUNE SPILLET\index-B2H4vrRz.js'
dst_file = r'c:\Users\josou\Downloads\NORSK AUTOTUNE SPILLET\assets\index-offline.js'

with open(src_file, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Point Bobba resources to local gordon folder
code = code.replace(
    'const IO="https://images.bobba.io/gordon/PRODUCTION-202006192205-424220153/"',
    'const IO="./gordon/PRODUCTION-202006192205-424220153/"'
)

# 2. Mock Firebase safe operations so no remote WebSocket is needed
# wt: return mock snapshot
code = code.replace(
    'function wt(t){t=Fn(t);const e=new EE(()=>{}),n=new Pm(e);return P3(t._repo,t,n).then(i=>new Gl(i,new oo(t._repo,t._path',
    'function wt(t){return Promise.resolve({exists:()=>false,val:()=>null});t=Fn(t);const e=new EE(()=>{}),n=new Pm(e);return P3(t._repo,t,n).then(i=>new Gl(i,new oo(t._repo,t._path'
)

# Ze: return no-op unlisten, invoke callback with empty snapshot
code = code.replace(
    'function Ze(t,e,n,i){return Nm(t,"value",e,n,i)}',
    'function Ze(t,e,n,i){try{e({exists:()=>false,val:()=>null})}catch{}return ()=>{}}'
)

# gn, rt: instant success
code = code.replace(
    'function gn(t,e){t=Fn(t),va("set",t._path),Oa("set",e,t._path,!1);',
    'function gn(t,e){return Promise.resolve();t=Fn(t),va("set",t._path),Oa("set",e,t._path,!1);'
)
code = code.replace(
    'function rt(t,e){gE("update",e,t._path);',
    'function rt(t,e){return Promise.resolve();gE("update",e,t._path);'
)

# 3. Patch Se action handler to handle game actions locally
se_orig = 'async function Se(t,e,n={}){const i=await ik(e,n);return i.state&&Tk(t,i.state),window.dispatchEvent(new Event("pocket-changed")),i.data}'
se_patch = '''async function Se(t,e,n={}){
  console.log("[OFFLINE ACTION]", e, n);
  if (e === "stab" || e === "deadlyStab") {
    try { new Audio("./sfx/osrs/stab.wav").play().catch(()=>{}); } catch{}
    t.blood = (t.blood || 0) + (e === "deadlyStab" ? 2000 : 500);
    window.dispatchEvent(new Event("pocket-changed"));
    pe(r ? "+500 blod!" : "+500 blood!");
    return { success: true };
  }
  if (e === "light") {
    try { new Audio("./sfx/osrs/light.wav").play().catch(()=>{}); } catch{}
    pe(r ? "Tændte den!" : "Lit up!");
    return { success: true };
  }
  if (e === "smoke" || e === "finishSmoke") {
    t.speedUntil = performance.now() + 120000;
    t.boostUntil = performance.now() + 120000;
    t.boostMult = 3;
    pe(r ? "Du er høj! 2x fart og 3x blod." : "You're high! 2x speed & 3x blood.");
    return { success: true };
  }
  if (e === "eat") {
    pe(r ? "Mmh lækker burger!" : "Delicious burger!");
    return { success: true };
  }
  if (e === "cdControl" || e === "cdInsert") {
    pe(r ? "CD sat i afspilleren!" : "CD loaded!");
    return { success: true };
  }
  return { success: true };
}'''

code = code.replace(se_orig, se_patch)

# 4. Patch dG try-catch block
start_str = 'try{const be=eU();i=be.stop,await Promise.all([Ka,LO(),F$(),sY(),mU(),pU(),gU()]);'
end_str = '"Log ud":"Log out")))));return}'

start_idx = code.find(start_str)
end_idx = code.find(end_str, start_idx) + len(end_str)
print(f"Found try-catch block from {start_idx} to {end_idx}")

dg_patch = '''try {
    await Promise.all([Ka.catch(()=>{}), sY().catch(()=>{}), mU().catch(()=>{})]);
  } catch(err){}
  n = {
    uid: "player_local",
    name: "Player",
    gender: "M",
    figure: "hd-180-10.hr-98113-9001.fa-98057.ch-98046-9004.lg-285-9004.sh-98143",
    blood: 1000000,
    owned: {},
    mixed: {},
    joinAt: Date.now(),
    vend: {},
    wardrobe: {},
    inventory: [
      { item: "machete" },
      { item: "knife" },
      { item: "gun" },
      { item: "weedseed", qty: 10 },
      { item: "wateringcan" },
      { item: "weed", qty: 25 },
      { item: "jointpaper", qty: 50 },
      { item: "bluntwrap", qty: 25 },
      { item: "joint", qty: 5 },
      { item: "blunt", qty: 5 },
      { item: "joint_thca", qty: 5 },
      { item: "lighter" },
      { item: "walkman" },
      { item: "cd_green" },
      { item: "cd_purple" },
      { item: "cd_red" },
      { item: "cd_yellow" },
      { item: "cd_album" },
      { item: "burger", qty: 10 },
      { item: "bandage", qty: 10 },
      { item: "mysterycase", qty: 5 },
      { item: "casekey", qty: 5 },
      { item: "pickaxe" },
      null, null, null, null, null
    ],
    stabs: {},
    syringeDay: 0,
    isAdmin: true,
    isMod: true,
    role: "admin",
    muteForever: false,
    banForever: false,
    ipBan: false,
    enterAnywhere: true,
    mutedUntil: 0,
    createdAt: Date.now(),
    seenDoor: true,
    nameColor: "#00ffcc",
    decorator: true,
    commands: true,
    sixty: { knifeAt: 0, syringeGiven: false },
    dumpsters: {},
    boostUntil: 0,
    boostMult: 2,
    speedUntil: 0,
    chemUntil: 0,
    lookKind: "",
    lookUntil: 0,
    deadlyLeft: 0,
    deadlyUntil: 0,
    speedMult: 2,
    leanUntil: 0,
    cupUntil: 0,
    shroomUntil: 0,
    catsCarved: 0,
    roomLevel: 5,
    storage: {},
    stash: {},
    tradeCap: { at: 0, n: 0 },
    noTradeLimit: true,
    tutorial: 5,
    questAt: 0,
    syringeSelfAt: 0,
    syringeBagAt: 0,
    vapeAt: 0,
    vapeUntil: 0,
    flappyAt: 0
  };'''

code = code[:start_idx] + dg_patch + code[end_idx:]

# 5. Replace startup trigger to call dG directly
startup_orig = 'document.title=n0;DE?(sD("Connecting…"),_O(),AP(Fo,t=>{fy.registering||oD(t)})):cG();let f2;'
startup_patch = 'document.title=n0; dG({ uid: "player_local", email: "player@hotel.local", isAnonymous: false, getIdToken: async() => "mock" }); let f2;'
code = code.replace(startup_orig, startup_patch)

# 6. Ensure default room navigation defaults to vt (Basement / Kælder)
code = code.replace(
    'ge("room",{roomId:hn(l.uid),arrival:"bed",intro:J})',
    'ge("room",{roomId:vt,from:vt})'
)

with open(dst_file, 'w', encoding='utf-8') as f:
    f.write(code)

print("Generated assets/index-offline.js successfully! Length:", len(code))
