<template>
    <el-form label-position="top" :model="FormData" style="max-width: 500px">
        <el-row>
            <el-col :span="12">
                <el-form-item label="当前等级" prop="Level" required>
                    <el-input
                        v-model.number="FormData.Level"
                        placeholder="当前粉丝牌等级"
                        type="text"
                        clearable
                    />
                </el-form-item>
            </el-col>
            <el-col :span="12">
                <el-form-item label="当前亲密度" prop="Exp">
                    <el-input
                        v-model.number="FormData.Exp"
                        placeholder="当前亲密度"
                        type="text"
                        clearable
                    />
                </el-form-item>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="12">
                <el-form-item label="目标等级" prop="tLevel" required>
                    <el-input
                        v-model.number="FormData.tLevel"
                        placeholder="目标粉丝牌等级"
                        type="text"
                        clearable
                    />
                </el-form-item>
            </el-col>
            <el-col :span="12">
                <el-form-item label="目标亲密度" prop="tExp">
                    <el-input
                        v-model.number="FormData.tExp"
                        placeholder="目标亲密度"
                        type="text"
                        clearable
                    />
                </el-form-item>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="12">
                <el-form-item label="每日获取" prop="DAILY" required>
                    <el-input
                        v-model.number="FormData.DAILY"
                        placeholder="每日获取亲密度"
                        type="text"
                        clearable
                    />
                </el-form-item>
            </el-col>
            <el-col :span="12">
                <el-form-item label="恢复初始值">
                    <el-button @click="restoreInitValue">重置</el-button>
                </el-form-item>
            </el-col>
        </el-row>
        <el-row class="description">
            <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                <span>每日获取</span>
                <el-tag type="success">{{ Result.DAILY }}</el-tag>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                <span>还需亲密度</span>
                <el-tag type="success">{{ Result.total }}</el-tag>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                <span>剩余天数</span>
                <el-tag type="success">{{ Result.days }}</el-tag>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                <span>目标日期</span>
                <el-tag type="success">{{ Result.target }}</el-tag>
            </el-col>
        </el-row>
    </el-form>
</template>

<script setup lang="ts">
import { reactive, watchEffect } from "vue";
import {
    ElRow,
    ElCol,
    ElForm,
    ElFormItem,
    ElInput,
    ElTag,
    ElMessage,
    ElButton,
} from "element-plus";
import ImportElementStyle from "./Funcs/ImportElementStyle";
import { leveMap, CalcIntimacy } from "./Funcs/CalcIntimacy";

const DefaultFormData = {
    Level: 1,
    Exp: 0,
    tLevel: 20,
    tExp: 0,
    DAILY: 1500,
};
const FormData = reactive({ ...DefaultFormData });
const Result = reactive({ DAILY: 0, total: 0, days: 0, target: "" });
const valueValidCheck = (obj) => {
    return (
        obj.Level >= 1 &&
        obj.Level <= 20 &&
        obj.tLevel >= 1 &&
        obj.tLevel <= 20 &&
        obj.Exp <= leveMap[obj.Level] &&
        obj.tExp <= leveMap[obj.tLevel] &&
        obj.DAILY >= 1 &&
        obj.DAILY <= 1500 &&
        obj.Level <= obj.tLevel
    );
};
const updateObject = (target, source) => {
    for (let key of Object.keys(source)) {
        target[key] = source[key];
    }
};
const updateResult = () => {
    if (!valueValidCheck(FormData)) {
        ElMessage({
            message: "值非法，请检查输入值",
            type: "warning",
        });
    } else {
        const r = CalcIntimacy({ ...FormData });
        updateObject(Result, r);
    }
};
const restoreInitValue = () => {
    ElMessage({
        message: "已恢复初始值",
        type: "success",
    });
    updateObject(FormData, DefaultFormData);
};
watchEffect(updateResult);
ImportElementStyle();
</script>

<style scoped>
.el-form-item {
    margin: 5px 5px 5px 5px;
}
.description {
    justify-content: center;
    margin: 10px 0px 10px 0px;
}
.description .el-col {
    display: flex;
    flex-direction: column;
}
.description span {
    margin: 5px 5px 5px 5px;
}
</style>
