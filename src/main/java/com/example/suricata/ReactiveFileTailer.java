package com.example.suricata;

import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Flux;
import reactor.core.publisher.FluxSink;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.file.*;

@Slf4j
public class ReactiveFileTailer {

    public static Flux<String> tail(Path path) {

        return Flux.create(emitter -> {

            try {
                WatchService watchService = FileSystems.getDefault().newWatchService();
                Path directory = path.getParent();
                directory.register(watchService,
                        StandardWatchEventKinds.ENTRY_MODIFY,
                        StandardWatchEventKinds.ENTRY_CREATE);

                Thread thread = new Thread(() -> followFile(path, watchService, emitter));
                thread.setDaemon(true);
                thread.start();

            } catch (IOException e) {
                emitter.error(e);
            }

        }, FluxSink.OverflowStrategy.BUFFER);
    }

    private static void followFile(Path path,
                                   WatchService watchService,
                                   FluxSink<String> emitter) {

        long position;

        try (RandomAccessFile file = new RandomAccessFile(path.toFile(), "r")) {

            position = file.length();
            file.seek(position);

            while (!emitter.isCancelled()) {

                String line;
                while ((line = file.readLine()) != null) {
                    emitter.next(line);
                }

                WatchKey key = watchService.take();

                for (WatchEvent<?> event : key.pollEvents()) {
                    Path changed = (Path) event.context();

                    if (changed.endsWith(path.getFileName())) {

                        long newLength = file.length();

                        if (newLength < position) {
                            log.info("File rotation: {}", path.toFile().getAbsolutePath());
                            file.seek(0);
                            position = 0;
                        }
                    }
                }

                key.reset();
                position = file.getFilePointer();
            }

        } catch (Exception e) {
            emitter.error(e);
        }
    }
}
