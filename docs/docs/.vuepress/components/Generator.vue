<template>
    <el-form label-position="top" style="max-width: 800px">
        <el-row v-for="(USER, index) of formData.USERS" :key="index">
            <UserOption v-bind="{ index, formData }"></UserOption>
            <FormItems
                ref="UserOptionsRef"
                v-bind="{ formData: USER, optionConfig: userOptionConfigs }"
            ></FormItems>
        </el-row>
        <el-divider />
        <el-row>
            <FormItems v-bind="{ formData, optionConfig: commonOptionConfigs }"></FormItems>
        </el-row>
        <el-divider />
        <el-button type="primary" @click="generate('json')">生成JSON</el-button>
        <el-button type="primary" @click="generate('yaml')">生成YAML</el-button>
        <el-button @click="restoreCache">清除缓存</el-button>
    </el-form>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { ElRow, ElForm, ElButton, ElDivider, ElMessage } from "element-plus";
import UserOption from "./BaseUI/UserOption.vue";
import FormItems from "./BaseUI/FormItems.vue";
import ImportElementStyle from "./Funcs/ImportElementStyle";
import { deepCopy, cache } from "./Funcs/Utils";
import { userOptionConfigs, commonOptionConfigs } from "./Config/GeneratorOptionConfigs";
import CopyText from "./Funcs/CopyText";
import json2yaml from "./Funcs/Json2Yaml";

const afterProcess = (data) => {
    if (data) {
        data["MOREPUSH"] = JSON.stringify(data["MOREPUSH"]);
        data["ASYNC"] === 1 ? (data["ASYNC"] = true) : (data["ASYNC"] = false);
        data["WEARMEDAL"] === 1 ? (data["WEARMEDAL"] = true) : (data["WEARMEDAL"] = false);
    }
    return data ?? undefined;
};

const defaultConfig = afterProcess(cache.get("json")) || {
    USERS: [
        {
            access_key: "",
            white_uid: 0,
            banned_uid: 0,
        },
    ],
    CRON: undefined,
    SENDKEY: undefined,
    MOREPUSH: undefined,
    PROXY: undefined,
    LIKE_CD: 2,
    SHARE_CD: 5,
    DANMAKU_CD: 6,
    WATCHINGLIVE: 65,
    SIGNINGROUP: 2,
    ASYNC: true,
    WEARMEDAL: false,
};

const formData = ref(deepCopy(defaultConfig));

const UserOptionsRef = ref<InstanceType<typeof FormItems>>();

const preProcess = (data) => {
    // turn `MOREPUSH` from string to object
    // turn `ASYNC` `WEARMEDAL` boolean to number
    try {
        data["MOREPUSH"] =
            data["MOREPUSH"] === "" || data["MOREPUSH"] === undefined
                ? undefined
                : JSON.parse(data["MOREPUSH"]);
    } catch (error) {
        ElMessage({
            type: "error",
            message: "请检查MOREPUSH值",
        });
        return null;
    }
    data["ASYNC"] === true ? (data["ASYNC"] = 1) : (data["ASYNC"] = 0);
    data["WEARMEDAL"] === true ? (data["WEARMEDAL"] = 1) : (data["WEARMEDAL"] = 0);
    return data;
};

const generate = (type: "json" | "yaml") => {
    const jsonData = preProcess(deepCopy(formData.value));
    if (type === "json") {
        jsonData &&
            UserOptionsRef.value[0].validCheck() &&
            CopyText(JSON.stringify(jsonData)) &&
            cache.set("json", jsonData);
    } else {
        const data = json2yaml(jsonData);
        jsonData && UserOptionsRef.value[0].validCheck() && CopyText(data);
    }
};

const restoreCache = () => {
    cache.remove("json");
    ElMessage({
        type: "success",
        message: "本地缓存已清除，即将刷新",
    });
    setTimeout(() => {
        if (typeof window !== 'undefined') {
            window.location.reload();
        }
    }, 1500);
};

ImportElementStyle();
</script>
