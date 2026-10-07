# FondFont 现成宠物模型调查 — 2026-10-07

状态：仅调查。未购买、未取得模型文件、未导出或在 hero 中测试。商品图是卖家的展示效果，不是本网站运行效果。

## 差距原因

目前网页宠物为我们自行编写 Blender 程序生成的网格，imagegen 只提供了造型参考。程序体块、解剖比例、毛发与表情没有达到参考图水准。骨骼与脚底数值检查通过不能证明视觉品质达标。后续应评估成品角色，而非继续小修当前体块。

## 候选

| 作者 / 角色 | 商品页标价，USD | 卖家描述 | 本次判断 |
| --- | --- | --- | --- |
| VFX Grace Golden Retriever + Orange white cat | 349 + 249，Individual 档；其他档另计 | 原生 Blender/Cycles，真实毛发、4K UDIM、控制骨骼；狗4段动画，猫3段行走/小跑/奔跑 | 展示图质感最好，视觉首选候选；实时毛发转换和许可待解决，不能保证导出即保留 Cycles 效果 |
| Nyilonelycompany Golden Retriever Puppy + Toyger Kitten | 50 + 40，Superhive 标价 | .blend、FBX；狗37段，猫23段；约3.82万/2.90万三角面，单材质4K | 更适合实时场景的幼宠组合；静态预览毛发、脸部仍低于 imagegen 参考，需要接受此风格取舍 |
| Animated3D Dog_B1 + Cat_B1 | 24.99 + 24.99 | .blend、FBX，60fps；狗16段，猫23段；没有 Control Rig | 成人金毛与三花猫组合；预览好于我们的体块，风格和幼宠参考不同；较弱的二次动画编辑条件 |

商品页价格不等于最终适用许可档位/税费。所有动画数量与文件参数均为卖家声明。本次查看了三组静态商品预览，没有成功核验视频播放或实际动画质量，不能据动作数量断言步态自然、摇尾巴可用。尿尿等定制动作也未证实包含。

## 原始来源 / 预览

- VFX Grace dog: https://www.vfxgrace.com/product/photorealistic-golden-retriever-rigged-3d-model-with-fur-and-animations/
- VFX Grace cat: https://www.vfxgrace.com/product/orange-white-cat-animation-blender-3d-model/
- VFX Grace dog image: https://www.vfxgrace.com/wp-content/uploads/2026/09/JF0O8Z0A_GoldenRetriever_Effect-map01-scaled.jpg
- VFX Grace cat image: https://www.vfxgrace.com/wp-content/uploads/2025/07/JW0P4U00_OrangeCat_sit_02-scaled.jpg
- Nyilonely dog: https://superhivemarket.com/products/golden-retriever-puppy
- Nyilonely cat: https://superhivemarket.com/products/kitten-toyger-cat
- Animated3D dog: https://superhivemarket.com/products/dog_b1
- Animated3D cat: https://superhivemarket.com/products/cat_b1

## 网页适配和许可

- Blender glTF 导出支持网格、Principled 材质、骨骼/形态键动画。原生 Cycles groom、UDIM 和复杂控制器不能仅凭存在 .blend 就视作已兼容，需要材质/毛发处理、动作烘焙和实际 GLB 检查。文档：https://docs.blender.org/manual/en/5.1/addons/import_export/scene_gltf2.html
- VFX Grace 许可明确列出网站用途，同时禁止独立文件分发，要求资源保护措施。公开可取的 GLB 如何满足条件须核实；不能将商用许可等同于任意公开模型交付许可。许可：https://www.vfxgrace.com/3d-models-license/
- Superhive Royalty Free 允许商业使用，但禁止未获授权再分发。网页 GLB 交付细节没有明确解释：https://superhivemarket.com/page/royalty-free-license
- 同作者猫在 Fab 有 listing，列出 Blender 与转换 GLB/glTF；具体许可和文件包应按实际购买页面核对：https://www.fab.com/listings/f63386c3-5a18-4bcd-99b4-caae3325ec9b
- Fab 标准许可摘要允许将素材融入项目商业分发并使用兼容工具，禁止独立再分发。未将其自动套用到其他平台的商品：https://www.fab.com/eula

## 采用建议

采用 advisor 的核心意见：先按视觉标准排序，再看适配难度；不以价格或动作数代替美术质量。VFX Grace 为视觉首选评估对象，Nyilonely 为幼宠实时风格备选；没有任何一套目前可称作已验证可上线。需要在现有 hero 镜头、太阳光照与实际显示尺寸下检查 GLB 后，才确认最终选择。

取得合法文件后，先做单只宠物的实际网页样片，验证毛发/轮廓、走路接地、转身、尾巴与移动端性能，再替换两只。保留随机游走和建筑避障逻辑，但不强行将现有程序步态套到专业骨骼上。
