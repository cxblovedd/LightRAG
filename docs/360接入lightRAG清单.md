| 名称           | 数据形态     | 是否推荐首批进入 LightRAG | 建议主键字段                   | 建议时间字段 |
| -------------- | ------------ | ------------------------- | ------------------------------ | ------------ |
| 病历资料       | 非结构化文本 | 是                        | patient_id、visit_id           | 文书时间     |
| 住院医嘱       | 结构化+文本  | 是                        | patient_id、visit_id、order_id | 开立时间     |
| 检查报告       | 半结构化文本 | 是                        | patient_id、exam_no            | 报告时间     |
| 检验报告       | 半结构化文本 | 是                        | patient_id、specimen_no        | 报告时间     |
| 体征记录       | 结构化       | 否                        | patient_id、record_id          | 记录时间     |
| 病历高拍       | 图片/PDF     | 否                        | patient_id、archive_id         | 归档时间     |
| 无纸化病案     | PDF/文本     | 是                        | patient_id、archive_id         | 归档时间     |
| 门诊处方       | 结构化       | 否                        | patient_id、prescription_id    | 开方时间     |
| 临床诊断       | 结构化+文本  | 是                        | patient_id、diagnosis_id       | 诊断时间     |
| 体检报告       | 半结构化文本 | 否                        | patient_id、report_id          | 体检时间     |
| 康复文书       | 非结构化文本 | 否                        | patient_id、doc_id             | 文书时间     |
| CDA文档        | XML/文本     | 是                        | patient_id、doc_id             | 文档时间     |
| 手麻记录       | 半结构化文本 | 是                        | patient_id、operation_id       | 手术时间     |
| 麻醉文书       | 非结构化文本 | 是                        | patient_id、doc_id             | 文书时间     |
| 麻醉相关       | 混合数据     | 否                        | patient_id、record_id          | 记录时间     |
| 关键指标       | 结构化       | 否                        | patient_id、metric_id          | 指标时间     |
| 护理文书弘爱   | 非结构化文本 | 是                        | patient_id、doc_id             | 文书时间     |
| 检查索引       | 索引结构化   | 否                        | patient_id、exam_no            | 检查时间     |
| 输血信息       | 结构化+文本  | 否                        | patient_id、transfusion_id     | 输血时间     |
| 过敏记录       | 结构化       | 否                        | patient_id、allergy_id         | 记录时间     |
| 治疗记录       | 半结构化文本 | 否                        | patient_id、treatment_id       | 治疗时间     |
| 医嘱闭环       | 执行日志     | 否                        | patient_id、exec_id            | 执行时间     |
| 血透记录单     | 半结构化文本 | 否                        | patient_id、dialysis_id        | 透析时间     |
| 放疗文书       | 非结构化文本 | 否                        | patient_id、doc_id             | 文书时间     |
| 重症文书       | 非结构化文本 | 是                        | patient_id、icu_doc_id         | 文书时间     |
| 门诊知情同意书 | PDF/文本     | 否                        | patient_id、consent_id         | 签署时间     |

来源于当前院内360患者全景模块整理。