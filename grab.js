function save(filename, data) {
    const blob = new Blob([data], {type: 'text/csv'});
    if(window.navigator.msSaveOrOpenBlob) {
        window.navigator.msSaveBlob(blob, filename);
    }
    else{
        const elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(blob);
        elem.download = filename;        
        document.body.appendChild(elem);
        elem.click();        
        document.body.removeChild(elem);
    }
}

points = plugin.fanfields.sortedFanpoints.map(point =>
	[
		point.point.x,
		point.point.y,
		map.unproject(point.point, plugin.fanfields.PROJECT_ZOOM).lat,
		map.unproject(point.point, plugin.fanfields.PROJECT_ZOOM).lng,
		window.portals[point.guid].options.data.title
			.replaceAll(',', ';')
	].join(',')
).join('\n')


save('points.csv', points)