import os
import math
import pygame
from graphics.weapon_skins import load_raw_skin, build_knife_sprite

# ==============================================================================
# HỆ THỐNG VIEWMODEL VŨ KHÍ 3D PHỐI CẢNH CHÂN THẬT NHẤT (TRUE 3D VIEWMODEL)
# ==============================================================================

# Màu sắc phong cách nhân vật hình khối Roblox (Classic Roblox Humanoid)
ROBLOX_YELLOW = (252, 215, 65)          # Màu vàng da Roblox kinh điển
ROBLOX_YELLOW_LIGHT = (255, 238, 110)    # Mặt sáng ngả vàng nhạt
ROBLOX_YELLOW_DARK = (205, 168, 38)      # Mặt tối / bóng đổ vàng đất
SLEEVE_BASE = (46, 52, 64)               # Áo đặc nhiệm xanh than Roblox
SLEEVE_LIGHT = (64, 72, 88)              # Mặt trên áo bắt sáng
SLEEVE_DARK = (28, 32, 40)               # Mặt bên hông áo tối
OUTLINE_COL = (20, 22, 28)               # Viền Cel-shading đen Roblox kinh điển


class CSViewModel:
    """
    Quản lý góc nhìn thứ nhất (FPS Viewmodel) 3D chân thật nhất:
    - Súng 3D có chiều sâu phối cảnh thực tế (True 3D Perspective Foreshortening):
      Đầu nòng ở xa thu nhỏ, báng súng ở gần mở to và trải dài theo trục mắt ngắm
    - Sống lưng súng 3D dập nổi (3D Top Rail / Picatinny Extrusion) có độ dày khối,
      rãnh ray kim loại, phay vát cạnh bắt sáng và họng nòng 3D (3D Muzzle Crown)
    - Cánh tay & bàn tay hình khối Roblox 3D ôm chặt báng súng và đỡ nòng súng
    - Đổi tay trái / phải mượt mà (cl_righthand 1 / 0)
    - Hoạt ảnh nạp đạn (Reload) nhịp nhàng và giật nòng nảy súng 3D khi khai hỏa (Recoil Kick)
    - Đầu nòng bắn đạn (muzzle_pos) trùng khớp 100% với nòng súng 3D thực tế
    """

    PISTOLS = {"CLASSIC", "GHOST", "SHERIFF"}
    MELEE = {"KNIFE"}

    WEAPON_CONFIGS = {
        "CLASSIC": {
            "len": 490, "angle": -11.0,
            "muzzle": (0.02, 0.05), "grip": (0.80, 0.65), "hg": None,
            "mag": (0.78, 0.85), "pos": (0.58, 0.52), "pistol": True, "sniper": False
        },
        "GHOST": {
            "len": 510, "angle": -11.0,
            "muzzle": (0.02, 0.14), "grip": (0.86, 0.62), "hg": None,
            "mag": (0.84, 0.82), "pos": (0.57, 0.52), "pistol": True, "sniper": False
        },
        "SHERIFF": {
            "len": 500, "angle": -12.0,
            "muzzle": (0.02, 0.12), "grip": (0.80, 0.65), "hg": None,
            "mag": (0.65, 0.45), "pos": (0.58, 0.52), "pistol": True, "sniper": False
        },
        "MP5": {
            "len": 620, "angle": -10.0,
            "muzzle": (0.02, 0.17), "grip": (0.76, 0.68), "hg": (0.34, 0.50),
            "mag": (0.48, 0.85), "pos": (0.54, 0.52), "pistol": False, "sniper": False
        },
        "UMP": {
            "len": 640, "angle": -10.0,
            "muzzle": (0.02, 0.15), "grip": (0.78, 0.65), "hg": (0.33, 0.45),
            "mag": (0.40, 0.88), "pos": (0.53, 0.52), "pistol": False, "sniper": False
        },
        "M014": {
            "len": 740, "angle": -9.0,
            "muzzle": (0.02, 0.15), "grip": (0.86, 0.70), "hg": (0.38, 0.50),
            "mag": (0.45, 0.70), "pos": (0.52, 0.52), "pistol": False, "sniper": False
        },
        "M1014": {
            "len": 740, "angle": -9.0,
            "muzzle": (0.02, 0.15), "grip": (0.86, 0.70), "hg": (0.38, 0.50),
            "mag": (0.45, 0.70), "pos": (0.52, 0.52), "pistol": False, "sniper": False
        },
        "MAG-7": {
            "len": 650, "angle": -10.0,
            "muzzle": (0.04, 0.44), "grip": (0.78, 0.68), "hg": (0.32, 0.58),
            "mag": (0.46, 0.88), "pos": (0.53, 0.52), "pistol": False, "sniper": False
        },
        "MAG7": {
            "len": 650, "angle": -10.0,
            "muzzle": (0.04, 0.44), "grip": (0.78, 0.68), "hg": (0.32, 0.58),
            "mag": (0.46, 0.88), "pos": (0.53, 0.52), "pistol": False, "sniper": False
        },
        "AK-47": {
            "len": 760, "angle": -9.0,
            "muzzle": (0.02, 0.20), "grip": (0.72, 0.65), "hg": (0.30, 0.42),
            "mag": (0.45, 0.88), "pos": (0.52, 0.51), "pistol": False, "sniper": False
        },
        "AK47": {
            "len": 760, "angle": -9.0,
            "muzzle": (0.02, 0.20), "grip": (0.72, 0.65), "hg": (0.30, 0.42),
            "mag": (0.45, 0.88), "pos": (0.52, 0.51), "pistol": False, "sniper": False
        },
        "VANDAL": {
            "len": 760, "angle": -9.0,
            "muzzle": (0.02, 0.20), "grip": (0.72, 0.65), "hg": (0.30, 0.42),
            "mag": (0.45, 0.88), "pos": (0.52, 0.51), "pistol": False, "sniper": False
        },
        "M416": {
            "len": 750, "angle": -9.0,
            "muzzle": (0.02, 0.25), "grip": (0.74, 0.66), "hg": (0.32, 0.45),
            "mag": (0.52, 0.88), "pos": (0.52, 0.51), "pistol": False, "sniper": False
        },
        "PHANTOM": {
            "len": 750, "angle": -9.0,
            "muzzle": (0.02, 0.25), "grip": (0.74, 0.66), "hg": (0.32, 0.45),
            "mag": (0.52, 0.88), "pos": (0.52, 0.51), "pistol": False, "sniper": False
        },
        "GUARDIAN": {
            "len": 760, "angle": -8.5,
            "muzzle": (0.02, 0.13), "grip": (0.76, 0.65), "hg": (0.30, 0.38),
            "mag": (0.50, 0.75), "pos": (0.52, 0.51), "pistol": False, "sniper": False
        },
        "M24": {
            "len": 780, "angle": -8.0,
            "muzzle": (0.02, 0.30), "grip": (0.82, 0.70), "hg": (0.32, 0.50),
            "mag": (0.56, 0.75), "pos": (0.51, 0.51), "pistol": False, "sniper": True
        },
        "AWM": {
            "len": 790, "angle": -8.0,
            "muzzle": (0.02, 0.24), "grip": (0.78, 0.68), "hg": (0.30, 0.48),
            "mag": (0.58, 0.75), "pos": (0.51, 0.51), "pistol": False, "sniper": True
        },
    }

    def __init__(self, screen_w=1600, screen_h=900):
        self.sw = screen_w
        self.sh = screen_h

        # Vị trí đầu nòng bắn đạn mặc định
        self.muzzle_pos = (self.sw * 0.58, self.sh * 0.52)

        # Trạng thái di chuyển, quán tính và bobbing
        self.bob_t = 0.0
        self.bob_x = 0.0
        self.bob_y = 0.0
        self.last_pos = (0.0, 0.0)
        self.sway_x = 0.0
        self.last_angle = 0.0
        self.last_time = 0.0

        # Cache các surface súng 3D đã dựng phối cảnh để đạt chuẩn 120 FPS
        self._3d_gun_cache = {}

    def _build_3d_gun_mesh(self, raw_skin, target_len, is_pistol=False, is_sniper=False):
        """
        Dựng mô hình súng 3D phối cảnh thực tế từ ảnh skin gốc:
        - Co giãn phối cảnh (Foreshortening): đầu nòng nhỏ (xa), báng súng to (gần mắt)
        - Đổ bóng mặt sườn và tạo độ dày khối sống lưng súng (3D Top Rail Extrusion)
        - Khắc các rãnh ray Picatinny kim loại và viền vát cạnh phản quang
        - Vành miệng nòng súng 3D hình elip (3D Muzzle Crown)
        """
        w, h = raw_skin.get_size()
        scale_x = target_len / float(w)
        target_h = int(h * scale_x)
        base_img = pygame.transform.smoothscale(raw_skin, (target_len, target_h))
        bw, bh = base_img.get_size()

        s_muzzle = 0.70 if is_pistol else (0.58 if is_sniper else 0.63)
        s_stock = 1.25 if is_pistol else (1.36 if is_sniper else 1.32)
        top_depth = 12 if is_pistol else 16

        pad_top = int(top_depth * 2.2) + 26
        pad_bot = int(bh * (s_stock - 1.0)) + 26
        out_w = bw + 42
        out_h = bh + pad_top + pad_bot
        out = pygame.Surface((out_w, out_h), pygame.SRCALPHA)

        strip_w = 2
        top_contour = []
        bore_y = int(bh * (0.12 if is_pistol else 0.22))

        # 1. Cắt lát và co giãn phối cảnh từng dải dọc (Perspective Slicing)
        for x in range(0, bw, strip_w):
            t = x / float(bw - 1)
            scale_y = s_muzzle + (s_stock - s_muzzle) * (t ** 1.05)
            sw = min(strip_w, bw - x)
            col = base_img.subsurface((x, 0, sw, bh))
            new_h = max(1, int(bh * scale_y))
            col_scaled = pygame.transform.smoothscale(col, (sw, new_h))

            # Đổ bóng nhẹ phần bụng dưới để tạo chiều sâu khối 3D
            darken = pygame.Surface((sw, new_h), pygame.SRCALPHA)
            darken.fill((18, 20, 26, int(22 * (1.0 - t) + 14 * t)))
            col_scaled.blit(darken, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

            draw_x = x
            draw_y = pad_top + int(bore_y * (scale_y - s_muzzle) * 0.3)
            out.blit(col_scaled, (draw_x, draw_y))

            # Tìm đỉnh cao nhất của dải để dựng sống lưng 3D
            mask_col = pygame.mask.from_surface(col_scaled, 35)
            for py in range(new_h):
                if mask_col.get_at((0, py)):
                    top_contour.append((draw_x, draw_y + py, scale_y, t))
                    break

        # 2. Dựng sống lưng súng 3D (3D Rail & Barrel Spine Extrusion)
        for i in range(len(top_contour) - 1):
            x1, y1, sc1, t1 = top_contour[i]
            x2, y2, sc2, t2 = top_contour[i + 1]

            # Dừng lại ở đuôi thân súng trước báng tì vai
            if t1 > 0.80:
                continue

            d1 = top_depth * sc1 * 0.70
            d2 = top_depth * sc2 * 0.70

            off_x1 = int(d1 * 0.35)
            off_y1 = -int(d1 * 0.85)
            off_x2 = int(d2 * 0.35)
            off_y2 = -int(d2 * 0.85)

            p1 = (x1, y1)
            p2 = (x2, y2)
            p3 = (x2 + off_x2, y2 + off_y2)
            p4 = (x1 + off_x1, y1 + off_y1)

            # Màu sắc kim loại phản quang theo vùng nòng / thân súng
            if t1 < 0.32:
                lum = int(75 + 32 * sc1)
                col_top = (lum, lum + 4, lum + 8)
            else:
                lum = int(42 + 28 * sc1)
                col_top = (lum, lum + 5, lum + 12)

            pygame.draw.polygon(out, col_top, [p1, p2, p3, p4])
            # Đường vát cạnh phản quang bắt sáng
            pygame.draw.line(out, (min(255, lum + 55), min(255, lum + 60), min(255, lum + 70)), p1, p2, 1)
            pygame.draw.line(out, (22, 25, 32), p4, p3, 1)

            # Rãnh răng ray Picatinny kim loại dọc thân súng
            if 0.34 <= t1 <= 0.78 and (int(x1) % 10) < 3:
                pygame.draw.line(out, (18, 20, 26), p1, p4, 2)
                pygame.draw.line(out, (165, 180, 200), (p1[0], p1[1] - 1), (p4[0], p4[1] - 1), 1)

        # 3. Họng nòng súng 3D (3D Muzzle Crown)
        if top_contour:
            mx, my, msc, _ = top_contour[0]
            crown_h = int(14 * msc)
            crown_w = int(6 * msc)
            crown_surf = pygame.Surface((crown_w * 2 + 4, crown_h + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(crown_surf, (20, 22, 26), (0, 0, crown_w * 2, crown_h))
            pygame.draw.ellipse(crown_surf, (155, 165, 180), (0, 0, crown_w * 2, crown_h), 2)
            pygame.draw.ellipse(crown_surf, (4, 4, 6), (crown_w // 2, crown_h // 4, crown_w, crown_h // 2))
            out.blit(crown_surf, (mx - crown_w, my))

        return out, pad_top, target_h

    def update(self, dt, player):
        now = pygame.time.get_ticks() / 1000.0
        frame_dt = min(0.08, max(0.0, now - self.last_time)) if self.last_time else 0.016
        self.last_time = now

        # Quán tính chuột nhẹ (Mouse sway)
        dang = (player.angle - self.last_angle + math.pi) % (2 * math.pi) - math.pi
        self.last_angle = player.angle
        target_sway = max(-10.0, min(10.0, -dang * 80.0))
        self.sway_x += (target_sway - self.sway_x) * min(1.0, frame_dt * 12.0)

        # Bobbing di chuyển chuẩn FPS
        dist_moved = math.hypot(player.x - self.last_pos[0], player.y - self.last_pos[1])
        self.last_pos = (player.x, player.y)
        is_moving = frame_dt > 0 and (dist_moved / frame_dt) > 20.0

        if is_moving:
            self.bob_t += frame_dt * 8.0
            self.bob_x = math.sin(self.bob_t) * 2.8
            self.bob_y = abs(math.cos(self.bob_t)) * 2.2
        else:
            self.bob_t += frame_dt * 1.5
            self.bob_x = math.sin(self.bob_t) * 0.6
            self.bob_y = abs(math.cos(self.bob_t)) * 0.8

    def _draw_poly(self, surf, pts, col_face, outline=True, lw=2):
        """Vẽ đa giác khối 3D với viền cel-shading chuẩn Roblox."""
        pygame.draw.polygon(surf, col_face, pts)
        if outline and lw > 0:
            pygame.draw.polygon(surf, OUTLINE_COL, pts, lw)

    def _draw_roblox_limb(self, surf, p_base, p_wrist, w_base, w_wrist, top_h=20, side_w=14):
        """Vẽ cánh tay hình khối Roblox 3D đa diện (Sleeve)."""
        bx, by = p_base
        wx, wy = p_wrist
        dx = wx - bx
        dy = wy - by
        L = math.hypot(dx, dy)
        if L < 1:
            return None, None
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux

        b_left = (bx - nx * (w_base / 2.0), by - ny * (w_base / 2.0))
        b_right = (bx + nx * (w_base / 2.0), by + ny * (w_base / 2.0))
        w_left = (wx - nx * (w_wrist / 2.0), wy - ny * (w_wrist / 2.0))
        w_right = (wx + nx * (w_wrist / 2.0), wy + ny * (w_wrist / 2.0))

        # Mặt trên bắt sáng
        w_left_top = (w_left[0] - top_h * 0.35, w_left[1] - top_h)
        b_left_top = (b_left[0] - top_h * 0.35, b_left[1] - top_h)
        self._draw_poly(surf, [b_left, w_left, w_left_top, b_left_top], SLEEVE_LIGHT)

        # Mặt bên hông đổ bóng
        w_right_side = (w_right[0] + nx * side_w, w_right[1] + ny * side_w)
        b_right_side = (b_right[0] + nx * side_w, b_right[1] + ny * side_w)
        self._draw_poly(surf, [b_right, w_right, w_right_side, b_right_side], SLEEVE_DARK)

        # Mặt chính diện
        self._draw_poly(surf, [b_left, w_left, w_right, b_right], SLEEVE_BASE)
        pygame.draw.line(surf, OUTLINE_COL, w_left, w_right, 3)

        return w_left, w_right

    def _draw_roblox_right_hand(self, surf, p_wrist, grip_pt, angle_deg, scale=1.15):
        """Vẽ bàn tay khối vàng Roblox ôm báng súng và siết cò."""
        gx, gy = grip_pt
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        def rot(lx, ly):
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            return gx + rx * scale, gy + ry * scale

        if p_wrist is not None:
            wx, wy = p_wrist
            wrist_pts = [(wx - 24, wy), (wx + 24, wy), rot(20, 24), rot(0, 20)]
            self._draw_poly(surf, wrist_pts, ROBLOX_YELLOW_DARK)

        palm = [rot(4, -20), rot(24, -16), rot(20, 24), rot(0, 20)]
        palm_top = [rot(4, -20), rot(24, -16), rot(20, -28), rot(0, -32)]
        self._draw_poly(surf, palm_top, ROBLOX_YELLOW_LIGHT)
        self._draw_poly(surf, palm, ROBLOX_YELLOW)

        thumb = [rot(-4, -22), rot(14, -20), rot(12, -10), rot(-6, -12)]
        self._draw_poly(surf, thumb, ROBLOX_YELLOW_LIGHT)

        for i in range(4):
            fy = -12 + i * 11
            f_pts = [rot(-20, fy), rot(2, fy - 1), rot(0, fy + 8), rot(-22, fy + 9)]
            self._draw_poly(surf, f_pts, ROBLOX_YELLOW)
            tip_pts = [rot(-22, fy), rot(-14, fy - 1), rot(-16, fy + 8), rot(-24, fy + 9)]
            self._draw_poly(surf, tip_pts, ROBLOX_YELLOW_LIGHT)

    def _draw_roblox_left_hand_rifle(self, surf, p_wrist, hg_pt, angle_deg, scale=1.15):
        """Vẽ bàn tay khối vàng Roblox đỡ phía dưới nòng/ốp tay súng trường."""
        hx, hy = hg_pt
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        def rot(lx, ly):
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            return hx + rx * scale, hy + ry * scale

        if p_wrist is not None:
            wx, wy = p_wrist
            wrist_pts = [(wx - 22, wy), (wx + 22, wy), rot(16, 26), rot(-24, 26)]
            self._draw_poly(surf, wrist_pts, ROBLOX_YELLOW_DARK)

        palm = [rot(-22, 4), rot(22, 4), rot(16, 26), rot(-24, 26)]
        palm_side = [rot(22, 4), rot(28, 8), rot(22, 30), rot(16, 26)]
        self._draw_poly(surf, palm_side, ROBLOX_YELLOW_DARK)
        self._draw_poly(surf, palm, ROBLOX_YELLOW)

        for i in range(3):
            fx = -18 + i * 14
            f_pts = [rot(fx, -14), rot(fx + 10, -14), rot(fx + 10, 6), rot(fx, 6)]
            self._draw_poly(surf, f_pts, ROBLOX_YELLOW)
            f_top = [rot(fx, -18), rot(fx + 10, -18), rot(fx + 10, -14), rot(fx, -14)]
            self._draw_poly(surf, f_top, ROBLOX_YELLOW_LIGHT)

    def _draw_roblox_pistol_hands(self, surf, r_wrist_pt, l_wrist_pt, grip_pt, angle_deg):
        """Vẽ hai tay khối Roblox cầm súng lục thế bắn 2 tay chuyên nghiệp."""
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        gx, gy = grip_pt

        def rot_p(lx, ly):
            return gx + (lx * cos_a - ly * sin_a), gy + (lx * sin_a + ly * cos_a)

        if r_wrist_pt is not None:
            wx, wy = r_wrist_pt
            self._draw_poly(surf, [(wx - 22, wy), (wx + 22, wy), rot_p(16, 20), rot_p(-12, 16)], ROBLOX_YELLOW_DARK)

        self._draw_poly(surf, [rot_p(4, -18), rot_p(22, -14), rot_p(18, 22), rot_p(0, 18)], ROBLOX_YELLOW)

        for i in range(3):
            fy = -10 + i * 11
            self._draw_poly(surf, [rot_p(-18, fy), rot_p(2, fy - 1), rot_p(0, fy + 8), rot_p(-20, fy + 9)], ROBLOX_YELLOW)

        if l_wrist_pt is not None:
            lwx, lwy = l_wrist_pt
            self._draw_poly(surf, [(lwx - 20, lwy), (lwx + 20, lwy), rot_p(-6, 42), rot_p(-30, 36)], ROBLOX_YELLOW_DARK)

        self._draw_poly(surf, [rot_p(-26, 18), rot_p(-4, 18), rot_p(-2, 38), rot_p(-28, 38)], ROBLOX_YELLOW)

    def draw(self, screen, player, reload_drop=0, side_sway=0, bomb_fuse=None):
        """Vẽ Viewmodel hoàn chỉnh lên màn hình và trả về tọa độ đầu nòng."""
        cur_w = getattr(player, "weapon", "CLASSIC").upper()
        righthand = getattr(player, "righthand", True)
        recoil = max(0.0, float(getattr(player, "recoil", 0.0)))

        # Ẩn viewmodel khi đang ngắm Scope
        if getattr(player, "scoped", False) and cur_w in ("AWM", "M24", "AK-47", "AK47", "VANDAL", "M416", "PHANTOM", "GUARDIAN", "UMP", "MP5"):
            self.muzzle_pos = (self.sw // 2, self.sh // 2)
            return self.muzzle_pos

        if cur_w == "KNIFE":
            return self._draw_knife_viewmodel(screen, player, righthand)
        elif cur_w in ("SMOKE", "MOLOTOV", "BOMB"):
            return self._draw_throwable_viewmodel(screen, player, cur_w, righthand, bomb_fuse)
        else:
            return self._draw_3d_gun_viewmodel(screen, player, cur_w, righthand, recoil, reload_drop, side_sway)

    # ==========================================================================
    # 1. VIEWMODEL SÚNG 3D PHỐI CẢNH CHÂN THẬT (TRUE 3D GUN VIEWMODEL)
    # ==========================================================================

    def _draw_3d_gun_viewmodel(self, screen, player, weapon_id, righthand, recoil, reload_drop, side_sway):
        cfg = self.WEAPON_CONFIGS.get(weapon_id, self.WEAPON_CONFIGS.get("AK-47"))
        raw_skin = load_raw_skin(weapon_id)
        if raw_skin is None:
            raw_skin = load_raw_skin("AK-47")
            if raw_skin is None:
                return self.muzzle_pos

        # Hiệu ứng nảy lùi Recoil theo trục 3D
        kick = min(1.0, recoil / 0.14)
        recoil_kick_y = int(14.0 * kick)
        recoil_kick_x = int(8.0 * kick)

        target_len = int(cfg["len"] * (self.sw / 1600.0))

        # Dựng hoặc nạp từ bộ đệm 3D Mesh
        cache_key = (weapon_id, target_len)
        if cache_key in self._3d_gun_cache:
            gun_3d_surf, pad_top, base_h = self._3d_gun_cache[cache_key]
        else:
            gun_3d_surf, pad_top, base_h = self._build_3d_gun_mesh(
                raw_skin, target_len, is_pistol=cfg["pistol"], is_sniper=cfg["sniper"]
            )
            self._3d_gun_cache[cache_key] = (gun_3d_surf, pad_top, base_h)

        # Góc nghiêng súng (khi nạp đạn thì hếch nhẹ góc)
        is_reloading = getattr(player, "reloading", False)
        reload_angle_add = -math.sin(min(1.0, max(0.0, reload_drop / 110.0)) * math.pi) * 8.0 if is_reloading else 0.0
        final_angle = cfg["angle"] + reload_angle_add

        # Xoay surface súng 3D
        gun_rot = pygame.transform.rotate(gun_3d_surf, final_angle)
        grw, grh = gun_rot.get_size()

        # Điểm neo súng trên màn hình
        base_anchor_x = int(self.sw * cfg["pos"][0])
        base_anchor_y = int(self.sh * cfg["pos"][1])

        anchor_x = int(base_anchor_x + self.bob_x + self.sway_x + side_sway + recoil_kick_x)
        anchor_y = int(base_anchor_y + self.bob_y + reload_drop + recoil_kick_y)

        gw, gh = gun_3d_surf.get_size()

        # Hàm tính tọa độ tương đối xoay quanh tâm ảnh
        def get_gun_point(local_ratio):
            if local_ratio is None:
                return None
            lx, ly = local_ratio
            rad = math.radians(final_angle)
            dx = (lx * target_len) - gw / 2.0
            dy = (pad_top + ly * base_h) - gh / 2.0
            rx = dx * math.cos(rad) + dy * math.sin(rad)
            ry = -dx * math.sin(rad) + dy * math.cos(rad)
            return anchor_x + rx + grw / 2.0, anchor_y + ry + grh / 2.0

        muzzle_pt = get_gun_point(cfg["muzzle"])
        grip_pt = get_gun_point(cfg["grip"])
        hg_pt = get_gun_point(cfg["hg"])

        vm_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)

        # ----------------------------------------------------------------------
        # A. VẼ TAY TRÁI (LEFT ARM & HAND)
        # ----------------------------------------------------------------------
        l_wrist_pt = None
        if not cfg["pistol"] and hg_pt is not None:
            l_base = (self.sw * 0.42, self.sh + 40)
            if is_reloading:
                rel_p = min(1.0, max(0.0, reload_drop / 110.0))
                l_wrist_pt = (hg_pt[0] - 10 + int(rel_p * 20), hg_pt[1] + 45 + int(rel_p * 70))
            else:
                l_wrist_pt = (hg_pt[0] - 12, hg_pt[1] + 46)

            self._draw_roblox_limb(vm_surf, l_base, l_wrist_pt, 130, 66)

        elif cfg["pistol"]:
            l_base = (self.sw * 0.52, self.sh + 40)
            l_wrist_pt = (grip_pt[0] - 18, grip_pt[1] + 52)
            self._draw_roblox_limb(vm_surf, l_base, l_wrist_pt, 120, 60)

        # ----------------------------------------------------------------------
        # B. VẼ TAY PHẢI (RIGHT ARM)
        # ----------------------------------------------------------------------
        r_base = (self.sw * 0.95, self.sh + 40)
        r_wrist_pt = (grip_pt[0] + 18, grip_pt[1] + 60)
        self._draw_roblox_limb(vm_surf, r_base, r_wrist_pt, 140, 72)

        # ----------------------------------------------------------------------
        # C. HIỂN THỊ MÔ HÌNH SÚNG 3D PHỐI CẢNH
        # ----------------------------------------------------------------------
        vm_surf.blit(gun_rot, (anchor_x, anchor_y))

        # ----------------------------------------------------------------------
        # D. BÀN TAY VÀNG ROBLOX ÔM CHẶT BÁNG SÚNG & NÒNG
        # ----------------------------------------------------------------------
        if cfg["pistol"]:
            self._draw_roblox_pistol_hands(vm_surf, r_wrist_pt, l_wrist_pt, grip_pt, final_angle)
        else:
            if not is_reloading and hg_pt is not None:
                self._draw_roblox_left_hand_rifle(vm_surf, l_wrist_pt, hg_pt, final_angle)
            self._draw_roblox_right_hand(vm_surf, r_wrist_pt, grip_pt, final_angle)

        # ----------------------------------------------------------------------
        # E. XUẤT LÊN MÀN HÌNH (LẬT GƯƠNG NẾU cl_righthand 0)
        # ----------------------------------------------------------------------
        if righthand:
            screen.blit(vm_surf, (0, 0))
            self.muzzle_pos = (int(muzzle_pt[0]), int(muzzle_pt[1]))
        else:
            flipped_vm = pygame.transform.flip(vm_surf, True, False)
            screen.blit(flipped_vm, (0, 0))
            self.muzzle_pos = (int(self.sw - muzzle_pt[0]), int(muzzle_pt[1]))

        return self.muzzle_pos

    # ==========================================================================
    # 2. VIEWMODEL DAO CẬN CHIẾN (KNIFE) KHỐI ROBLOX
    # ==========================================================================

    def _draw_knife_viewmodel(self, screen, player, righthand):
        knife_raw = build_knife_sprite()
        if knife_raw is None:
            return self.muzzle_pos

        swing_timer = getattr(player, "knife_swing", 0.0)
        is_stab = getattr(player, "knife_is_stab", False)
        swing_total = 0.28

        anim_off_x = 0
        anim_off_y = 0
        rot_angle = -45.0

        if swing_timer > 0:
            prog = 1.0 - (swing_timer / swing_total)
            p = math.sin(prog * math.pi)
            if is_stab:
                anim_off_x = -int(p * 85)
                anim_off_y = -int(p * 95)
                rot_angle = -40.0 - p * 15.0
            else:
                rot_angle = -45.0 - p * 55.0
                anim_off_x = -int(p * 90)
                anim_off_y = int(math.cos(prog * math.pi) * 35)

        target_w = int(self.sw * 0.36)
        rw, rh = knife_raw.get_size()
        target_h = max(1, int(rh * target_w / rw))
        knife_scaled = pygame.transform.smoothscale(knife_raw, (target_w, target_h))
        knife_rot = pygame.transform.rotate(knife_scaled, rot_angle)
        krw, krh = knife_rot.get_size()

        anchor_x = int(self.sw * 0.68 + self.bob_x + self.sway_x + anim_off_x)
        anchor_y = int(self.sh * 0.50 + self.bob_y + anim_off_y)

        rad = math.radians(rot_angle)
        dx = (0.85 * target_w) - target_w / 2.0
        dy = (0.50 * target_h) - target_h / 2.0
        rx = dx * math.cos(rad) + dy * math.sin(rad)
        ry = -dx * math.sin(rad) + dy * math.cos(rad)
        grip_pt = (anchor_x + rx + krw / 2.0, anchor_y + ry + krh / 2.0)

        mx = (0.05 * target_w) - target_w / 2.0
        my = (0.50 * target_h) - target_h / 2.0
        m_rx = mx * math.cos(rad) + my * math.sin(rad)
        m_ry = -mx * math.sin(rad) + dy * math.cos(rad)
        tip_pt = (anchor_x + m_rx + krw / 2.0, anchor_y + m_ry + krh / 2.0)

        vm_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)

        r_base = (self.sw * 0.96, self.sh + 40)
        r_wrist_pt = (grip_pt[0] + 16, grip_pt[1] + 55)
        self._draw_roblox_limb(vm_surf, r_base, r_wrist_pt, 135, 70)

        vm_surf.blit(knife_rot, (anchor_x, anchor_y))

        self._draw_roblox_right_hand(vm_surf, r_wrist_pt, grip_pt, rot_angle, scale=1.05)

        if righthand:
            screen.blit(vm_surf, (0, 0))
            self.muzzle_pos = (int(tip_pt[0]), int(tip_pt[1]))
        else:
            flipped_vm = pygame.transform.flip(vm_surf, True, False)
            screen.blit(flipped_vm, (0, 0))
            self.muzzle_pos = (int(self.sw - tip_pt[0]), int(tip_pt[1]))

        return self.muzzle_pos

    # ==========================================================================
    # 3. VIEWMODEL VẬT PHẨM NÉM (SMOKE, MOLOTOV, BOMB) KHỐI ROBLOX
    # ==========================================================================

    def _draw_throwable_viewmodel(self, screen, player, item_kind, righthand, bomb_fuse=None):
        """Vẽ tay khối Roblox cầm lựu đạn khói, bom xăng hoặc bom hẹn giờ."""
        vm_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)

        gx = int(self.sw * 0.65 + self.bob_x + self.sway_x)
        gy = int(self.sh * 0.60 + self.bob_y)

        r_base = (self.sw * 0.95, self.sh + 40)
        r_wrist_pt = (gx + 18, gy + 75)
        self._draw_roblox_limb(vm_surf, r_base, r_wrist_pt, 135, 70)

        font = pygame.font.SysFont("Arial", 18, bold=True)
        if item_kind == "SMOKE":
            pygame.draw.rect(vm_surf, (75, 80, 90), (gx - 20, gy - 30, 52, 85), border_radius=6)
            pygame.draw.rect(vm_surf, (240, 210, 50), (gx - 20, gy - 8, 52, 14))
            pygame.draw.rect(vm_surf, (50, 55, 62), (gx - 5, gy - 48, 22, 20), border_radius=3)
            pygame.draw.circle(vm_surf, (200, 200, 210), (gx - 10, gy - 40), 8, 2)
            lbl = font.render("SMOKE", True, (240, 240, 245))
            vm_surf.blit(lbl, (gx - 16, gy + 15))
        elif item_kind == "MOLOTOV":
            pygame.draw.rect(vm_surf, (40, 110, 70), (gx - 18, gy - 20, 48, 80), border_radius=8)
            pygame.draw.rect(vm_surf, (40, 110, 70), (gx - 3, gy - 50, 18, 32))
            pygame.draw.rect(vm_surf, (200, 190, 170), (gx - 5, gy - 60, 22, 14))
            fl_sz = int(14 + 6 * math.sin(pygame.time.get_ticks() * 0.02))
            pygame.draw.circle(vm_surf, (255, 120, 20), (gx + 6, gy - 70), fl_sz)
            pygame.draw.circle(vm_surf, (255, 230, 40), (gx + 6, gy - 70), max(2, fl_sz // 2))
            lbl = font.render("FIRE", True, (255, 200, 60))
            vm_surf.blit(lbl, (gx - 10, gy + 15))
        elif item_kind == "BOMB":
            pygame.draw.circle(vm_surf, (32, 35, 42), (gx + 6, gy + 10), 46)
            pygame.draw.circle(vm_surf, (60, 65, 75), (gx - 4, gy), 14)
            pygame.draw.rect(vm_surf, (10, 12, 16), (gx - 18, gy - 4, 50, 24), border_radius=4)
            f_val = f"{max(0.0, bomb_fuse):.1f}s" if (bomb_fuse is not None and bomb_fuse > 0) else "5.0s"
            t_col = (255, 40, 40) if (pygame.time.get_ticks() // 200) % 2 == 0 else (255, 180, 40)
            digi = font.render(f_val, True, t_col)
            vm_surf.blit(digi, (gx + 7 - digi.get_width() // 2, gy - 1))

        grip_pt = (gx + 6, gy + 15)
        self._draw_roblox_right_hand(vm_surf, r_wrist_pt, grip_pt, -8.0, scale=1.1)

        if righthand:
            screen.blit(vm_surf, (0, 0))
            self.muzzle_pos = (gx, gy)
        else:
            flipped_vm = pygame.transform.flip(vm_surf, True, False)
            screen.blit(flipped_vm, (0, 0))
            self.muzzle_pos = (self.sw - gx, gy)

        return self.muzzle_pos
