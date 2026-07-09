import map from 'postcss-map';

export default {
	plugins: [
		map({
			basePath: 'src',
			maps: ['themes.json']
		})
	]
};
