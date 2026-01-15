import { getFormattedTimestamp } from '../utils.js';

const AUTO_DOC_URL = 'https://samsung.doc.lfdev.io/autodoc';
const AutoDocRead_URL = `${AUTO_DOC_URL}/read`;
const AutoDocID = 643;

export default async function AutoDocPage(page, screenshotDir) {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    try {
        const url = `${AutoDocRead_URL}/${AutoDocID}`;
        console.log('AutoDoc_URL:', url);
        
        await page.goto(url, { waitUntil: 'networkidle' });
        const timestamp = getNewTimestamp();
        await page.screenshot({path: `${screenshotDir}/${timestamp}_autodoc.png`});
        
        return { success: true, message: 'AutoDoc 생성 완료' };
    } catch (error) {
        console.error(`Error in createAutoDoc: ${error.message}`);
        return { success: false, message: `Error in createAutoDoc: ${error.message}` };
    }
}
