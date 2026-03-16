// @ts-ignore
import { ElMessage } from "element-plus";

export default function copyText(text: string): boolean {
    if (typeof window === 'undefined' || typeof navigator === 'undefined') {
        return false;
    }

    try {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text); // use navigator.clipboard
        } else {
            var textarea = document.createElement("textarea");
            document.body.appendChild(textarea);
            // hide this input area
            textarea.style.position = "fixed";
            textarea.style.clip = "rect(0 0 0 0)";
            textarea.style.top = "10px";
            // execute
            textarea.value = text;
            textarea.select();
            document.execCommand("copy", true);
            // remove the input area
            document.body.removeChild(textarea);
        }
        ElMessage({
            type: "success",
            message: "配置文件已复制到剪切板",
        });
        return true;
    } catch (err) {
        console.log(err);
        return false;
    }
}
