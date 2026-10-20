"""DeskShelf ALL-IN-ONE (2026-10-20): one Fusion document with the current shelf v2.4c, modules v2,
MagSafe v3 and all four accessory sets (v1). Each set = one top-level component; the copies of the
shelf that every accessory assembly carries are deleted, only the set's own parts and its REF
objects stay. Source f3d files are only read. Collisions between sets are expected (storage hangers
vs backlight brackets on rod 5)."""
import adsk.core, adsk.fusion, json, traceback

E = "/Users/YOU/fusion-mcp/exports/"
OUT = "/Users/YOU/fusion-mcp/exports/deskshelf-all-in-one"
NAME = "DeskShelf ALL - v2.4c + modules + MagSafe + accessories (2026-10-20)"
SETS = [  # (component name, f3d, keep rule)
    ("01 Shelf v2.4c", "deskshelf-v2.4c/deskshelf_v2_4c.f3d", None),
    ("02 Modules v2 (MacBook, books, Mac mini)", "deskshelf-v2.3-modules-v2/deskshelf_v2_3_modules_v2.f3d",
     ("laptop_dock", "bookend", "macmini_stand", "REF - MacBook", "REF - textbooks", "REF - Mac mini", "REF - wall")),
    ("03 MagSafe v3", "magsafe-mount-v3/deskshelf_v2_3_magsafe_v3.f3d", ("magsafe_", "REF - Puck", "REF - Phone")),
    ("04 Gridfinity in drawers", "acc-gridfinity/deskshelf_gridfinity.f3d", ("gf_",)),
    ("05 Front rod - plug holders + USB hub", "acc-front-rod/deskshelf_v2_3_front_rod_acc_v1.f3d",
     ("acc_", "REF - USB hub", "REF - Plugs", "REF - Keyboard")),
    ("06 Storage - cable tray, tool rail, headphones", "acc-storage/deskshelf_acc_storage_v1.f3d",
     ("tray_", "tool_rail", "hp_", "REF - power", "REF - PSU", "REF - headphones")),
    ("07 Backlight - LED rail + ESP32", "acc-backlight/deskshelf_backlight_v1.f3d", ("acc_backlight", "REF - backlight")),
]


def run(context):
    app = adsk.core.Application.get()
    rep = {"sets": []}
    try:
        for d in list(app.documents):
            if d.name.startswith("DeskShelf ALL"):
                d.close(False)
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        des = adsk.fusion.Design.cast(app.activeProduct)
        des.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = des.rootComponent
        im = app.importManager
        for label, f3d, keep in SETS:
            before = root.occurrences.count
            im.importToTarget(im.createFusionArchiveImportOptions(E + f3d), root)
            assert root.occurrences.count == before + 1, label
            occ = root.occurrences.item(root.occurrences.count - 1)
            comp = occ.component
            comp.name = label
            removed = []
            if keep:
                for ch in [comp.occurrences.item(i) for i in range(comp.occurrences.count)]:
                    if not ch.component.name.startswith(keep):
                        removed.append(ch.name)
                        ch.deleteMe()
            kept = [comp.occurrences.item(i).name for i in range(comp.occurrences.count)]
            rep["sets"].append({"set": label, "kept": kept, "removed": len(removed)})
        # Accessory test/reference helpers that only clutter the view.
        doc.name = NAME
        app.activeViewport.fit()
        import os
        os.makedirs(OUT, exist_ok=True)
        des.exportManager.execute(des.exportManager.createFusionArchiveExportOptions(OUT + "/deskshelf_all_in_one.f3d"))
        app.activeViewport.saveAsImageFile(OUT + "/preview_all.png", 1600, 1000)
        rep["ok"] = True
    except Exception:
        rep["error"] = traceback.format_exc()
    json.dump(rep, open("/Users/YOU/fusion-mcp/all-in-one/build_report.json", "w"), indent=1, ensure_ascii=False)
