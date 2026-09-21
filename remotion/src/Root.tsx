import React from "react";
import { Composition } from "remotion";
import { AnnotatedVideo } from "./AnnotatedVideo";
import { ModuleVideo } from "./ModuleVideo";
import { demoAnnotated } from "./modules/demo-annotated";
import { module01 } from "./modules/module-01";
import type { ModuleConfig } from "./types";

const FPS = 30;

/** Add a module by importing its config and listing it here. */
const MODULES: ModuleConfig[] = [module01];

export const RemotionRoot: React.FC = () => (
  <>
    {MODULES.map((config) => (
      <Composition
        key={config.id}
        id={config.id}
        component={ModuleVideo}
        durationInFrames={Math.round(config.durationInSeconds * FPS)}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{ config }}
      />
    ))}
    <Composition
      id={demoAnnotated.id}
      component={AnnotatedVideo}
      durationInFrames={Math.round(demoAnnotated.durationInSeconds * FPS)}
      fps={FPS}
      width={1920}
      height={1080}
      defaultProps={{ config: demoAnnotated }}
    />
  </>
);
