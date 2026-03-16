<template>
    <el-col v-bind="optionConfig.col" v-for="option of optionConfig.items" :key="option.prop">
        <el-form-item>
            <template #label>
                <div class="label">
                    {{ option.name }}
                    <div>
                        <ElTooltip v-if="option.info" :content="option.info" placement="top-start">
                            <el-icon :size="iconSize"><ChatDotSquare /></el-icon>
                        </ElTooltip>
                        <ElTooltip v-if="option.required" content="必填项" placement="top-start">
                            <el-icon :size="iconSize" class="required">
                                <Warning />
                            </el-icon>
                        </ElTooltip>
                    </div>
                </div>
            </template>
            <el-checkbox
                v-if="option.style === 'check'"
                v-model="formData[option.prop]"
                :placeholder="'请输入' + option.prop"
                :label="option.prop"
                size="large"
                border
            ></el-checkbox>
            <el-input
                v-if="option.style === 'input'"
                v-model="formData[option.prop]"
                @change="onInputChange($event, option)"
                :type="option.type"
                :placeholder="'请输入' + option.prop"
            >
                option.name
            </el-input>
        </el-form-item>
    </el-col>
</template>

<script lang="ts" setup>
import type { PropType } from "vue";
import { ElMessage } from "element-plus";
import type { IConfig } from "../types";
import { ElCol, ElFormItem, ElTooltip, ElIcon, ElInput, ElCheckbox } from "element-plus";
import { ChatDotSquare, Warning } from "@element-plus/icons-vue";

const iconSize = 20;
const props = defineProps({
    formData: {
        required: true,
    },
    optionConfig: {
        required: true,
        type: Object as PropType<IConfig>,
    },
});
const onInputChange = (value, option) => {
    // modify string to number
    if (option.type === "number") {
        props.formData[option.prop] = parseInt(value);
    }
};

const validCheck = () => {
    // check valid in self domain
    const { optionConfig } = props;
    for (const item of optionConfig.items) {
        const flag =
            item.required &&
            (props.formData[item.prop] === undefined || props.formData[item.prop] === "");
        if (!flag) continue;
        else {
            ElMessage({
                type: "error",
                message: "请填写必填值" + item.name,
            });
            return false;
        }
    }
    return true; // 验证完毕
};

defineExpose({
    validCheck,
});
</script>

<style scoped>
.el-form-item {
    margin: 5px 5px 5px 5px;
}
.label {
    display: flex;
    justify-content: space-between;
}
.required {
    color: var(--el-color-danger);
}
</style>
