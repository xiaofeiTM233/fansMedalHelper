<template>
    <el-col :xs="24" :sm="3" :md="3" :lg="3" :xl="3">
        <div class="option">
            <el-tag :closable="index !== 0" @close="onTagClose(index)" class="info" type="success">
                用户 {{ index + 1 }}
            </el-tag>
            <el-check-tag
                v-show="index + 1 == formData.USERS.length"
                checked
                class="add"
                @click="addUser"
            >
                +
            </el-check-tag>
        </div>
    </el-col>
</template>

<script setup>
import { ElCol, ElTag, ElCheckTag } from "element-plus";
import { deepCopy } from "../Funcs/Utils";
const props = defineProps({
    index: {
        require: true,
        type: Number,
    },
    formData: {
        require: true,
    },
});
const onTagClose = (index) => props.formData.USERS.splice(index, 1);
const addUser = () =>
    props.formData.USERS.push(
        deepCopy({
            access_key: "",
            white_uid: 0,
            banned_uid: 0,
        }),
    );
</script>

<style scoped>
.el-col {
    display: flex;
    align-items: center;
}
.option {
    display: flex;
    flex-direction: column;

    width: 100%;
}
.option * {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 5px;
    height: 10px;
}
.option .info {
    height: 50px;
}
</style>
