# TODO fixes
# - Refactoring/cleanup
# - Convert os.system to subprocess
# - Full type hints
# - Normalize image font and density based on area of map
# - Escaping symbols for LaTeX
# - Too many portals overflowing table
# - Argv stuff
# TODO features
# - Rebuilding information

from collections import defaultdict
from random import randint
from math import ceil
import os
import argparse

class Point:
	def __init__(self, xx : float, yy : float, la : float, lo : float, n : str):
		self.lat = la
		self.long = lo
		self.x = xx
		self.y = yy
		self.name = n

	def __str__(self):
		return '%s: (%f, %f)' % (self.name, self.x, self.y)

	def __repr__(self):
		return self.__str__()

	def __sub__(self, other):
		return Point(self.x - other.x, self.y - other.y, 0, 0, '')

	# For the purposes of sorting all elements are equal
	def __lt__(self, other):
		return False

class Geometry:
	EPS = 1e-9

	@staticmethod
	def cross(p1, p2):
		return p1.x * p2.y - p2.x * p1.y

	@staticmethod
	def cross3(p1, p2, p3):
		return Geometry.cross(p2 - p1, p3 - p1)

	@staticmethod
	def convexHull(_pts):
		pts = list(_pts) # Pass by value
		pts.sort(key = lambda p: (p.x, p.y))
		stack = []

		for times in range(2):
			for pt in pts:
				while len(stack) >= 2:
					top = stack[-1]
					sec = stack[-2]
					if Geometry.cross3(sec, top, pt) > 0:
						stack.pop()
					else:
						break
				stack.append(pt)

			pts.pop()
			pts.sort(key = lambda p :(-p.x, -p.y))

		stack.pop()
		return stack
	
	@staticmethod
	def dist(p1, p2):
		return (p1.x - p2.x)**2 + (p1.y - p2.y)**2

	@staticmethod
	def in_triangle(tri, q):
		p1, p2, p3 = tri
		total = abs(Geometry.cross3(p1, p2, p3))
		sub = sum([
			abs(Geometry.cross3(p1, p2, q)),
			abs(Geometry.cross3(p2, p3, q)),
			abs(Geometry.cross3(p3, p1, q))
		])
		return abs(total - sub) < Geometry.EPS

class MaxField:
	@staticmethod
	def sbul(n):
		if n <= 8:
			return 0
		s = ceil((n - 8) / 8)
		if s > 2:
			return 99
		return s

	@staticmethod
	def extra_hacks(n):
		if n <= 2:
			return 0
		return ceil((n - 2) / 2)

	@staticmethod
	def triangulate(_pts, tri, level=1):
		p1, p2, p3 = tri
		pts = list(_pts)

		if len(pts) == 0:
			return []

		q = pts[randint(0, len(pts) - 1)]

		subtri = [
			(p1, p2, q),
			(p2, p3, q),
			(p3, p1, q)
		]

		links = [(p1, q, level), (p2, q, level), (p3, q, level)]

		for s_tri in subtri:
			links += MaxField.triangulate(
				filter(lambda p: Geometry.in_triangle(s_tri, p) and p != q, pts),
				s_tri,
				level + 1
			)

		return links

	@staticmethod
	def zigzag(hull, pts):
		links = []
		cur = 0
		next_for = 2
		next_back = len(hull) - 1
		i = 0

		for j in range(len(hull)):
			links.append((hull[j], hull[(j + 1) % len(hull)], 0))

		while i < len(hull) - 2:
			if i % 2 == 0:
				links.append((hull[cur], hull[next_for], 0))
				triangle = (hull[cur], hull[next_for], hull[next_for - 1])
				links += MaxField.triangulate(
					filter(lambda p: Geometry.in_triangle(triangle, p) and p not in triangle, pts),
					triangle
				)
				cur = next_for
				next_for += 1
			else:
				links.append((hull[cur], hull[next_back], 0))
				triangle = (hull[cur], hull[next_back], hull[(next_back + 1) % len(hull)])
				links += MaxField.triangulate(
					filter(lambda p: Geometry.in_triangle(triangle, p) and p not in triangle, pts),
					triangle
				)
				cur = next_back
				next_back -= 1
		
			i += 1

		return links

	keys_req = defaultdict(int)
	links_out = defaultdict(int)

	@staticmethod
	def plan(_pts, _links, first=0):
		global keys_req
		global links_out
		keys_req = defaultdict(int)
		links_out = defaultdict(int)
		link_log = []

		pts = list(_pts)
		links = list(_links)
		start = pts[first]
		pts.sort(key = lambda p: Geometry.dist(p, start))
		result = list(pts)
		order = {}
		for i in range(len(pts)):
			order[pts[i]] = i
		vist = set()
		freq = defaultdict(int)

		for i in range(len(links)):
			p1, p2, level = links[i]
			if order[p1] < order[p2]:
				links[i] = (p1, p2, level)
			else:
				links[i] = (p2, p1, level)

		for link in links:
			p1, p2, level = link
			freq[p1] += 1
			keys_req[p1] += 1
			links_out[p2] += 1

		for p in pts:
			row_log = [order[p], p.name, freq[p]]

			links_back = []
			for link in links:
				p1, p2, level = link
				if p2 == p:
					links_back.append(link)
			links_back.sort(key = lambda p: p[2])

			link_log.append(row_log + [list(map(lambda l: l[0].name, links_back))])

		return result, link_log

	@staticmethod
	def tsp(_pts):
		pts = list(_pts)
		par = [i for i in range(len(pts))]
		adj = [[] for i in range(len(pts))]
		key_log = []

		def find(ind):
			if par[ind] == ind:
				return ind
			par[ind] = find(par[ind])
			return par[ind]

		edges = []
		for i in range(len(pts)):
			for j in range(i + 1, len(pts)):
				edges.append((Geometry.dist(pts[i], pts[j]), i, j))

		edges.sort()

		for edge in edges:
			d, u, v = edge
			r = find(u)
			s = find(v)
			if r != s:
				par[r] = s
				adj[u].append(v)
				adj[v].append(u)

		walk = []

		def dfs(u, p):
			walk.append(u)
			for v in adj[u]:
				if v == p:
					continue
				dfs(v, u)
				walk.append(u)

		dfs(0, -1)

		vist = set()
		path = []
		for u in walk:
			if u in vist:
				continue
			path.append(u)
			vist.add(u)

		result = []

		for i in range(len(path)):
			pt = pts[path[i]]
			key_log.append((path[i], pt.name, keys_req[pt]))

		for i in range(len(path) - 1):
			result.append((pts[path[i]], pts[path[i + 1]], 0))

		return result, key_log	   

	@staticmethod
	def normalize(pts : Point):
		minX = min([p.x for p in pts])
		minY = min([p.y for p in pts])

		for i in range(len(pts)):
			pts[i].x -= minX - 2
			pts[i].y -= minY - 2

	@staticmethod
	def compute(filename, num_trials):
		with open(filename, 'r') as f:
			lines = f.read().strip().splitlines()
		points = []

		for line in lines:
			xx, yy, la, lo, n = line.split(',')
			points.append(Point(float(xx), float(yy), float(la), float(lo), n))

		MaxField.normalize(points)

		ch = Geometry.convexHull(points)

		trials = []

		for i in range(num_trials):
			links = MaxField.zigzag(ch, points)
			sorted_points, link_info = MaxField.plan(points, links, randint(0, len(points) - 1))
			tsp_path, key_info = MaxField.tsp(sorted_points)
			sbul_burden = sum(map(lambda p: MaxField.sbul(links_out[p]), points))
			hack_burden = sum(map(lambda p: MaxField.extra_hacks(keys_req[p]), points))
			#trials.append((sbul_burden, hack_burden, sorted_points, links, tsp_path))
			trials.append((sbul_burden, hack_burden, key_info, link_info, links, tsp_path, sorted_points))

		trials.sort(key = lambda t: (t[0], t[1]))
		best = trials[0]
		sorted_points = best[6]
		sorted_lines = []
		for i in range(len(sorted_points) - 1):
			sorted_lines.append((sorted_points[i], sorted_points[i + 1], 0))
		print(best[0], best[1])

		Render.render_svg(sorted_points, best[5], False, 'key_scout')
		Render.render_svg(sorted_points, sorted_lines, False, 'field_order')
		Render.render_svg(sorted_points, best[4], False, 'fields')
		Render.latex(best[2], best[3], best[0])

class Render:
	@staticmethod
	def render_svg(pts, lines, full=False, filename='render'):
		maxX = max([p.x for p in pts])
		maxY = max([p.y for p in pts])

		header = '''
			<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">
			<style>
			.ptext {
				font: 4px Verdana;
			}
			</style>
		'''.strip() % (int(maxX) + 10, int(maxY) + 2)
		footer = '</svg>'

		shapes = []

		for l in lines:
			p1 = l[0]
			p2 = l[1]
			shapes.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke-width="0.25" stroke="blue" />' % (p1.x, p1.y, p2.x, p2.y))

		for p in pts:
			shapes.append('<circle cx="%d" cy="%d" r="%d" />' % (p.x, p.y, 1))
			name = '. ' + p.name if full else ''
			shapes.append('<text x="%d" y="%d" class="ptext" font-family="Verdana" font-size="4px">%d%s</text>' % (p.x + 1, p.y + 1, pts.index(p), name))

		code = '\n'.join([header] + shapes + [footer])
		with open(filename + '.svg', 'w') as f:
			f.write(code)

	@staticmethod
	def latex_escape(s : str):
		return s.replace('#', '\\#')

	@staticmethod
	def latex(key_info, link_info, sbuls):
		header = '''
			\\documentclass{article}
			\\usepackage[margin=0.2in]{geometry}
			\\usepackage{amssymb}
			\\usepackage{graphicx}

			\\begin{document}
		'''

		footer = '''
			\\onecolumn
			\\newpage
			\\section*{Key Scout Path}
			\\includegraphics[width=\\textwidth]{key_scout}
			\\newpage
			\\section*{Field Creation Path}
			\\includegraphics[width=\\textwidth]{field_order}
			\\newpage
			\\section*{Final Field Map}
			SoftBank Ultra Links Required: %d \\\\
			\\includegraphics[width=\\textwidth]{fields}

			\\end{document}
		''' % sbuls

		key_table = '''
			\\begin{tabular}{c|r|l|c}
				& \\textbf{ID} & \\textbf{Portal Name} & \\textbf{Keys} \\\\
				\\hline \\hline
				%s
			\\end{tabular}
			\\newpage
			\\twocolumn
		''' % '\\\\\n\n'.join(map(
			lambda row: '&'.join(
				map(
					lambda col: str(col).replace('&', '\\&')[:50],
					('$\\square$',) + row
				)
			),
			key_info))

		link_text = '''
			\\\\
			%s
		'''

		link_sections = ''.join(map(
			lambda row: '''
				\\subsection*{%d) %s}
				%d key(s) required. %s
			''' % (row[0], row[1], row[2], link_text % '\n'.join(map(
				lambda val: '$\\square$\\ ' + val + '\\\\',
				row[3]
			)) if len(row[3]) > 0 else ''
			),
			link_info
		))

		result = Render.latex_escape(header + key_table + link_sections + footer)
		with open('plan.tex', 'w') as f:
			f.write(result)

		os.system('convert -density 500 key_scout.svg key_scout.png')
		os.system('convert -density 500 field_order.svg field_order.png')
		os.system('convert -density 500 fields.svg fields.png')
		os.system('pdflatex plan.tex')


if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument('filename', nargs='?', default='points.csv')
	args = arg_parser.parse_args()

	MaxField.compute(args.filename, 1000)