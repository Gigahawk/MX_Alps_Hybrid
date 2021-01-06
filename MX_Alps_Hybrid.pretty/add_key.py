import glob
import re

HOLE_RE = re.compile(r"\(pad \"\" np_thru_hole circle \(at ([\d\.-]+) ([\d\.-]+)\s{0,1}[\d]*\) \(size 3\.9878 3\.9878\) \(drill 3\.9878\).*")

# Hack to make str.format() work
KPR = "{KIPRJMOD}"

KEY_STR = """  (model ${kpr}/MX_Alps_Hybrid/MX.3dshapes/mx_switch.step
    (at (xyz {center} 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
"""

NOLED_STR = """  (model ${kpr}/MX_Alps_Hybrid/MX.3dshapes/mx_switch_no_led.step
    (at (xyz {center} 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
"""

STAB_STR = """  (model ${kpr}/MX_Alps_Hybrid/MX.3dshapes/mx_stab.step
    (offset (xyz {center} 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 {rotate}))
  )
"""

for path in glob.iglob(r"*.kicad_mod"):
    print(path)
    if "ledonly" in path.lower():
        print("Skipping led only footprint")
        continue

    with open(path, 'r') as f:
        data = f.read()
        f.seek(0)
        lines = f.readlines()

    matches = HOLE_RE.findall(data)
    if not matches:
        print("No holes found, skipping")
        continue
    matches = [float(m[0]) for m in matches]
    abs_matches = [abs(m) for m in matches]

    min_idx = abs_matches.index(min(abs_matches))
    # Internal units are inches for whatever reason
    center = matches[min_idx] / 25.4
    if center.is_integer():
        center = int(center)
    if "overlay" in path.lower():
        center = None
        min_idx = -1

    stabs = []
    for i in range(len(matches)):
        if i == min_idx:
            continue
        s = float(matches[i])
        if s.is_integer():
            s = int(s)
        stabs.append(s)

    print(f"Holes at {matches}")
    print(f"Center at {center}")
    print(f"Stabs at {stabs}")

    if center is not None:
        if "noled" in path.lower():
            key_str = NOLED_STR.format(kpr=KPR, center=center)
        else:
            key_str = KEY_STR.format(kpr=KPR, center=center)
    else:
        key_str = ""

    if key_str:
        if key_str in data:
            print("Keycap model already found, not inserting")
        else:
            key_lines = key_str.splitlines(True)
            lines[-1:-1] = key_lines
    else:
        print("Keycap center not found, not inserting")

    if "reversedstabilizers" in path.lower():
        rotate = 180
    else:
        rotate = 0
    for s in stabs:
        stab_str = STAB_STR.format(kpr=KPR, center=s, rotate=rotate)
        stab_lines = stab_str.splitlines(True)
        lines[-1:-1] = stab_lines

    with open(path, 'w') as f:
        f.writelines(lines)
