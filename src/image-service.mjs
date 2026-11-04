import sharpService from 'astro/assets/services/sharp';
import sharp from 'sharp';

export default {
  ...sharpService,
  getURL(options, config) {
    return `${sharpService.getURL(options, config)}&icc=1`;
  },
  async transform(input, options, config) {
    const metadata = await sharp(input).metadata();
    // Icon Composer's 16-bit PNGs otherwise lose their profile before WebP encoding.
    if (metadata.icc && metadata.depth === 'ushort') {
      input = await sharp(input).withIccProfile('srgb').png().toBuffer();
    }
    return sharpService.transform(input, options, config);
  },
};
