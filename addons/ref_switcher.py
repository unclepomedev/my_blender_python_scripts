import bpy, re

KEY = "SEMI_COLON"
PAT_FRONT = re.compile(r"^front[_ ]?(\d+)$", re.IGNORECASE)
PAT_SIDE = re.compile(r"^side[_ ]?(\d+)$", re.IGNORECASE)
SCENE_PROP = "ref_cycle_index"


def _collect_pairs():
    fronts, sides = {}, {}
    for o in bpy.data.objects:
        m = PAT_FRONT.match(o.name)
        if m:
            fronts[int(m.group(1))] = o
            continue
        m = PAT_SIDE.match(o.name)
        if m:
            sides[int(m.group(1))] = o
    indices = sorted(set(fronts.keys()) | set(sides.keys()))
    return fronts, sides, indices


def _show_only_index(idx, fronts, sides, indices):
    for i in indices:
        if i in fronts:
            _set_visible(fronts[i], False)
        if i in sides:
            _set_visible(sides[i], False)
    if idx in fronts:
        _set_visible(fronts[idx], True)
    if idx in sides:
        _set_visible(sides[idx], True)


def _set_visible(obj, vis=True):
    obj.hide_set(not vis)
    obj.hide_render = not vis


class WmOtCycleRefPair(bpy.types.Operator):
    bl_idname = "wm.cycle_reference_pair"
    bl_label = "Cycle Reference Pair"

    def execute(self, context):
        fronts, sides, indices = _collect_pairs()
        if not indices:
            self.report({"WARNING"}, "No objects named front_<n> / side_<n> found.")
            return {"CANCELLED"}

        scene = context.scene
        curr = scene.get(SCENE_PROP, None)

        if curr in indices:
            pos = indices.index(curr)
            nxt = indices[(pos + 1) % len(indices)]
        else:
            nxt = indices[0]

        _show_only_index(nxt, fronts, sides, indices)
        scene[SCENE_PROP] = nxt
        self.report({"INFO"}, f"Showing front_{nxt} / side_{nxt} (if present)")
        return {"FINISHED"}


addon_keymaps = []


def register():
    bpy.utils.register_class(WmOtCycleRefPair)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon or wm.keyconfigs.user
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.cycle_reference_pair", KEY, "PRESS")
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(WmOtCycleRefPair)


if __name__ == "__main__":
    register()
