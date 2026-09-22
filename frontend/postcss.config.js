import map from 'postcss-map';
import path from 'path';
import { fileURLToPath } from 'url';

export default {
	plugins: [
		map({
			basePath: path.resolve(path.dirname(fileURLToPath(import.meta.url)), 'src'),
			maps: ['themes.json']
		})
	]
};
